from typing import Any, Callable
import serial, threading, time, crc8, struct, serial.tools.list_ports, math
from .State import SERVOS_PIN

from .Logger import Logger
from .Shapes import OrientedPoint


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
        self._teensy = None
        self.crc = crc
        self._crc8 = crc8.crc8()
        self.last_message = None
        self.end_bytes = b"\xBA\xDD\x1C\xC5"
        self.l = Logger()

        for port in serial.tools.list_ports.comports():
            if port.vid == vid and port.pid == pid and int(port.serial_number) == ser:
                self._teensy = serial.Serial(port.device, baudrate=baudrate)
                break
        if self._teensy == None:
            if dummy:
                self.l.log("Dummy mode", 1)
            else:
                self.l.log("No Teensy found !", 3)
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
                    self.l.log("Invalid CRC8, sending NACK ... ", 1)
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
                    1,
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
                self.l.log("Received message handling crashed :\n" + str(e.args), 2)
                time.sleep(0.5)


class RollingBasis(Teensy):
    ######################
    # Rolling basis init #
    ######################
    def __init__(
        self,
        ser=12678590,
        vid: int = 5824,
        pid: int = 1155,
        baudrate: int = 115200,
        crc: bool = True,
        dummy: bool = False,
    ):
        super().__init__(ser, vid, pid, baudrate, crc, dummy)
        # All position are in the form tuple(X, Y, THETA)
        self.odometrie = OrientedPoint(0.0, 0.0, 0.0)
        self.position_offset = OrientedPoint(0.0, 0.0, 0.0)
        self.current_action = None
        """
        This is used to match a handling function to a message type.
        add_callback can also be used.
        """
        self.messagetype = {
            128: self.rcv_odometrie,  # \x80
            129: self.rcv_action_finish,  # \x81
            130: self.rcv_print,  # \x82
            255: self.unknowed_msg,
        }

        self.queue = []

    #####################
    # Position handling #
    #####################
    def true_pos(self, position: OrientedPoint) -> OrientedPoint:
        """
        _summary_

        :param position: _description_
        :type position: OrientedPoint
        :return: _description_
        :rtype: OrientedPoint
        """
        return position + self.position_offset

    #############################
    # Received message handling #
    #############################
    def rcv_print(self, msg: bytes):
        self.l.log("Teensy says : " + msg.decode("ascii", errors="ignore"))

    def rcv_odometrie(self, msg: bytes):
        self.odometrie = OrientedPoint(
            struct.unpack("<f", msg[0:4])[0],
            struct.unpack("<f", msg[4:8])[0],
            struct.unpack("<f", msg[8:12])[0],
        )

    def rcv_action_finish(self, msg: bytes):
        self.l.log("Action finished : " + msg.hex())
        if not self.queue or len(self.queue) == 0:
            self.l.log("Received action_finished but no action in queue", 1)
            return
        # remove the action that just finished
        for i in range(len(self.queue)):
            if list(self.queue[i].keys())[0] == msg:
                self.l.log(f"Removing action {i} from queue : " + str(self.queue[i]))
                self.queue.pop(i)
                break
        if len(self.queue) == 0:
            self.l.log("Queue is empty")
            self.current_action = None
            return
        self.send_bytes(list(self.queue[0].values())[0])
        self.current_action = list(self.queue[0].keys())[0]
        self.l.log("Sending next action in queue")

    def unknowed_msg(self, msg: bytes):
        self.l.log(f"Teensy does not know the command {msg.hex()}", 1)

    #########################
    # User facing functions #
    #########################

    class Command:
        GoToPoint = b"\x00"
        CurveGoTo = b"\x01"
        KeepCurrentPosition = b"\02"
        DisablePid = b"\03"
        EnablePid = b"\04"
        ResetPosition = b"\05"
        SetPID = b"\06"
        SetHome = b"\07"
        Stop = b"\x7E"  # 7E = 126
        Invalid = b"\xFF"

    @Logger
    def Go_To(
        self,
        position: OrientedPoint,
        *,  # force keyword arguments
        skip_queue=False,
        is_backward: bool = False,
        max_speed: int = 150,
        next_position_delay: int = 100,
        action_error_auth: int = 50,
        traj_precision: int = 50,
        correction_trajectory_speed: int = 80,
        acceleration_start_speed: int = 80,
        acceleration_distance: float = 10,
        deceleration_end_speed: int = 80,
        deceleration_distance: float = 10,
    ) -> None:
        """
        Va à la position donnée en paramètre

        :param position: la position en X et Y (et theta)
        :type position: OrientedPoint
        :param is_backward: en avant (false) ou en arrière (true), defaults to False
        :type direction: bool, optional
        :param speed: Vitesse du déplacement, defaults to b'\x64'
        :type speed: bytes, optional
        :param next_position_delay: delay avant la prochaine position, defaults to 100
        :type next_position_delay: int, optional
        :param action_error_auth: l'erreur autorisé dans le déplacement, defaults to 20
        :type action_error_auth: int, optional
        :param traj_precision: la précision du déplacement, defaults to 50
        :type traj_precision: int, optional
        """
        pos = self.true_pos(position)
        msg = (
            self.Command.GoToPoint
            + struct.pack("<f", pos.x)
            + struct.pack("<f", pos.y)
            + struct.pack("<?", is_backward)
            + struct.pack("<B", max_speed)
            + struct.pack("<H", next_position_delay)
            + struct.pack("<H", action_error_auth)
            + struct.pack("<H", traj_precision)
            + struct.pack("<B", correction_trajectory_speed)
            + struct.pack("<B", acceleration_start_speed)
            + struct.pack("<f", acceleration_distance)
            + struct.pack("<B", deceleration_end_speed)
            + struct.pack("<f", deceleration_distance)
        )
        # https://docs.python.org/3/library/struct.html#format-characters
        if skip_queue or len(self.queue) == 0:
            self.queue.insert(0, {self.Command.GoToPoint: msg})
            self.send_bytes(msg)
        else:
            self.queue.append({self.Command.GoToPoint: msg})

    @Logger
    def curve_go_to(
        self,
        destination: OrientedPoint,
        corde: float,
        interval: int,
        *,  # force keyword arguments
        skip_queue=False,
        direction: bool = False,
        speed: int = 150,
        next_position_delay: int = 100,
        action_error_auth: int = 20,
        traj_precision: int = 50,
        test: bool = False,
    ) -> None:
        """Go to a point with a curve"""

        middle_point = OrientedPoint(
            (self.odometrie.x + destination.x) / 2,
            (self.odometrie.y + destination.y) / 2,
        )
        # alpha est l'angle entre la droite (position, destination) et l'axe des ordonnées (y)
        alpha = math.atan2(
            destination.y - self.odometrie.y, destination.x - self.odometrie.x
        )
        # theta est l'angle entre la droite (position, destination) et l'axe des abscisses (x)
        theta = math.pi / 2 - alpha

        third_point = OrientedPoint(
            middle_point.x + math.cos(theta) * corde,
            middle_point.y + math.sin(theta) * corde,
        )

        center = calc_center(self.odometrie, third_point, destination)
        destination = self.true_pos(destination)
        center = self.true_pos(center)
        if test:
            return center
        curve_msg = (
            self.Command.CurveGoTo  # command
            + struct.pack("<ff", destination.x, destination.y)  # target_point
            + struct.pack("<ff", center.x, center.y)  # center_point
            + struct.pack("<H", interval)  # interval (distance between two points)
            + struct.pack("<?", direction)  # direction
            + struct.pack("<H", speed)  # speed
            + struct.pack("<H", next_position_delay)  # delay
            + struct.pack("<H", action_error_auth)  # error_auth
            + struct.pack("<H", traj_precision)  # precision
        )
        if skip_queue or len(self.queue) == 0:
            self.l.log("Skipping Queue ...")
            self.queue.insert(0, {self.Command.CurveGoTo: curve_msg})
            self.l.log(self.queue)
            self.send_bytes(curve_msg)
        else:
            self.queue.append({self.Command.CurveGoTo: curve_msg})

    @Logger
    def Keep_Current_Position(self, skip_queue=False):
        msg = self.Command.KeepCurrentPosition
        if skip_queue:
            self.queue.insert(0, {self.Command.KeepCurrentPosition: msg})
            self.send_bytes(msg)
        else:
            self.queue.append({self.Command.KeepCurrentPosition: msg})

    @Logger
    def Disable_Pid(self, skip_queue=False):
        msg = self.Command.DisablePid
        if skip_queue or len(self.queue) == 0:
            self.queue.insert(0, {self.Command.DisablePid: msg})
            self.send_bytes(msg)
        else:
            self.queue.append({self.Command.DisablePid: msg})

    @Logger
    def Enable_Pid(self, skip_queue=False):
        msg = self.Command.EnablePid
        if skip_queue or len(self.queue) == 0:
            self.queue.insert(0, {self.Command.EnablePid: msg})
            self.send_bytes(msg)
        else:
            self.queue.append({self.Command.EnablePid: msg})

    @Logger
    def Reset_Odo(self, skip_queue=False):
        msg = self.Command.ResetPosition
        if skip_queue or len(self.queue) == 0:
            self.queue.insert(0, {self.Command.ResetPosition: msg})
            self.send_bytes(msg)
        else:
            self.queue.append({self.Command.ResetPosition: msg})

    def Set_Home(self, x, y, theta, *, skip_queue=False):
        msg = self.Command.SetHome + struct.pack("<fff", x, y, theta)
        if skip_queue or len(self.queue) == 0:
            self.queue.insert(0, {self.Command.SetHome: msg})
            self.send_bytes(msg)
        else:
            self.queue.append({self.Command.SetHome: msg})

    def Set_PID(self, Kp: float, Ki: float, Kd: float, skip_queue=False):
        msg = self.Command.SetPID + struct.pack("<fff", Kp, Ki, Kp)
        if skip_queue or len(self.queue) == 0:
            self.queue.insert(0, {self.Command.SetPID: msg})
            self.send_bytes(msg)
        else:
            self.queue.append({self.Command.SetPID: msg})


class Actuators(Teensy):
    def __init__(
        self,
        vid: int = 5824,
        pid: int = 1155,
        baudrate: int = 115200,
        crc: bool = True,
        pin_servos: list[int] = SERVOS_PIN,
    ):
        super().__init__(vid, pid, baudrate, crc)
        self.pin_servos = pin_servos

    class Command:  # values must correspond to the one defined on the teensy
        ServoGoTo = b"\x01"

    def __str__(self) -> str:
        return self.__class__.__name__

    #########################
    # User facing functions #
    #########################

    @Logger
    def servo_go_to(
        self, pin: int, angle: int, min_angle: int = 0, max_angle: int = 180
    ):
        if angle >= min_angle and angle <= max_angle:
            msg = (
                self.Command.ServoGoTo
                + struct.pack("<B", pin)
                + struct.pack("B", angle)
            )
            # https://docs.python.org/3/library/struct.html#format-characters
            self.send_bytes(msg)
        else:
            print(
                f"you tried to write {angle}° on pin {pin} wheras angle must be between {min_angle} and {max_angle}°"
            )
