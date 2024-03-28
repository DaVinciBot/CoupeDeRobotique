from typing import Any, Callable
import serial, threading, time, crc8, serial.tools.list_ports
from logger import Logger, LogLevels
from geometry import OrientedPoint
from teensy_comms.dummy_serial import DummySerial


# TODO: n'a pas trop ça place ici voir pour déplacer
# Used for curve_go_to
# DO NOT REMOVE
def calc_tmp(a: OrientedPoint, b: OrientedPoint) -> float:
    return (a.x**2 - b.x**2 + a.y**2 - b.y**2) / (2 * (a.y - b.y))


def frac_tmp(a: OrientedPoint, b: OrientedPoint) -> float:
    return (a.x - b.x) / (a.y - b.y)


def calc_center(a: OrientedPoint, b: OrientedPoint, c: OrientedPoint) -> OrientedPoint:
    """
    Permet de calculer le centre d'un cercle passant par 3 points
    https://cral-perso.univ-lyon1.fr/labo/fc/Ateliers_archives/ateliers_2005-06/cercle_3pts.pdf

    Attention, pour qu'il n'y ai pas de division par 0, les deux premiers points doivent avoir des ordonnées différentes (a.y != b.y)
    Même s'il a une permutation au cas où, il est préférable de que les ordonnées soient différentes
    """
    if a.y == b.y:
        a, b = b, c
    if a == b or a == c or b == c:  # not a circle
        return a
    x_c = (calc_tmp(c, b) - calc_tmp(b, a)) / (frac_tmp(b, a) - frac_tmp(c, b))
    center = OrientedPoint(
        (-x_c),
        (frac_tmp(b, a) * x_c + calc_tmp(b, a)),
    )
    return center


class TeensyException(Exception):
    pass


class Teensy:
    def __init__(
        self,
        logger: Logger,
        ser: int,
        vid: int = 0x16C0,
        pid: int = 0x0483,
        baudrate: int = 115200,
        crc: bool = True,
        dummy: bool = False,
    ):
        """
        Crée un objet Serial Teensy, qui permet la communication entre le code et la carte
        Si vous ne savez pas ce que vous faites, ne changez que le paramètre `ser`

        Exemple:
        ```py
        carte = Teensy(123456)
        carte.send_bytes(...)
        ```

        Les paramètres vid et pid permettent de restreindre la recherche au teensy,
        le paramètre ser permet de choisir parmis les teensy

        :param ser: Numéro de Série
        :type ser: int
        :param vid: _description_, defaults to 0x16C0
        :type vid: int, optional
        :param pid: _description_, defaults to 0x0483
        :type pid: int, optional
        :param baudrate: _description_, defaults to 115200
        :type baudrate: int, optional
        :param crc: _description_, defaults to True
        :type crc: bool, optional
        :param dummy: _description_, defaults to False
        :type dummy: bool, optional
        :raises TeensyException: _description_
        """
        self._teensy = DummySerial()
        self.crc = crc
        self._crc8 = crc8.crc8()
        self.last_message = None
        self.end_bytes = b"\xBA\xDD\x1C\xC5"
        self.l = Logger(identifier="Teensy")

        for port in serial.tools.list_ports.comports():
            if (
                port.vid == vid
                and port.pid == pid
                and port.serial_number is not None
                and int(port.serial_number) == ser
            ):
                self._teensy = serial.Serial(port.device, baudrate=baudrate)
                break
        if self._teensy is None:
            if dummy:
                self.l.log("Dummy mode", self.l.log_level.INFO)
                self._teensy = DummySerial()
            else:
                self.l.log("No Teensy found !", self.l.log_level.CRITICAL)
                raise TeensyException("No Device !")
        self.messagetype = {}
        if not dummy:
            self._reciever = threading.Thread(
                target=self.__receiver__, name="TeensyReceiver"
            )
            self._reciever.start()

    def send_dummy(self, type):
        """
        Send false data to trigger the teensy to send data back
        """
        # TODO: utiliser if else au lieu de match car pas compatible avec python 3.9
        match (type):
            case "bad_crc":
                self._teensy.reset_output_buffer()
                msg = b"\xFF\xFF\xEE\x66"
                self.last_message = msg
                self._teensy.write(msg + bytes([len(msg)]) + b"\x00" + self.end_bytes)
                while self._teensy.out_waiting:
                    pass
                return
            case "bad_length":
                self._teensy.reset_output_buffer()
                msg = b"\xFF\xFF\xEE\x66"
                self._teensy.write(
                    msg + bytes([len(msg) + 1]) + b"\x00" + self.end_bytes
                )
                while self._teensy.out_waiting:
                    pass
                return
            case "bad_id":
                self._teensy.reset_output_buffer()
                msg = b"\x2F\xFF\xEE\x66"
                msg += bytes([len(msg)])
                self._crc8.reset()
                self._crc8.update(msg)
                msg += self._crc8.digest()
                self._crc8.reset()
                self._teensy.write(msg + self.end_bytes)
                while self._teensy.out_waiting:
                    pass
                return
            case "send_nack":
                self._teensy.reset_output_buffer()
                msg = b"\x7F"
                msg += bytes([len(msg)])
                self._crc8.reset()
                self._crc8.update(msg)
                msg += self._crc8.digest()
                self._crc8.reset()
                self._teensy.write(msg + self.end_bytes)
                while self._teensy.out_waiting:
                    pass
                return

    def send_bytes(self, data: bytes):
        self.last_message = data
        self._teensy.reset_output_buffer()
        msg = data + bytes([len(data)])
        if self.crc:
            self._crc8.reset()
            self._crc8.update(msg)
            msg += self._crc8.digest()
            self._crc8.reset()

        self._teensy.write(msg + self.end_bytes)
        while self._teensy.out_waiting:
            pass

    def read_bytes(self) -> bytes:
        return self._teensy.read_until(self.end_bytes)

    def add_callback(self, func: Callable[[bytes], None], id: int):
        self.messagetype[id] = func

    def __receiver__(self) -> None:
        """This is started as a thread, handles the data according to the decided format :

        msg_type | msg_data | msg_length | CRC8 | MSG_END_BYTES
        size : 1 | msg_length | 1 | 1 | 4

        The size is in bytes.
        It will call the corresponding function
        """
        while True:
            msg = self.read_bytes()

            if self.crc:
                crc = msg[-5:-4]
                msg = msg[:-5]
                self._crc8.reset()
                self._crc8.update(msg)
                if self._crc8.digest() != crc:
                    self.l.log("Invalid CRC8, sending NACK ... ", LogLevels.WARNING)
                    self.send_bytes(b"\x7F")  # send NACK
                    self._crc8.reset()
                    continue
                self._crc8.reset()

            else:
                msg = msg[:-4]

            lenmsg = msg[-1]

            if lenmsg > len(msg):
                self.l.log(
                    "Received Teensy message that does not match declared length "
                    + msg.hex(sep=" "),
                    LogLevels.WARNING,
                )
                continue
            try:
                if msg[0] == 127:
                    self.l.log("Received a NACK")
                    if self.last_message != None:
                        self.send_bytes(self.last_message)
                        self.l.log(f"Sending back action : {self.last_message[0]}")
                        self.last_message = None
                else:
                    self.messagetype[msg[0]](msg[1:-1])
            except Exception as e:
                self.l.log(
                    "Received message handling crashed :\n" + str(e),
                    LogLevels.ERROR,
                )
                time.sleep(0.5)
