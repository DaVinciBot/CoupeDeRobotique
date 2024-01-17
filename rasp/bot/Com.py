from typing import Any, Callable
import serial, threading, time, crc8, struct, serial.tools.list_ports, math
from .State import SERVOS_PIN

from .Logger import Logger
from .Shapes import OrientedPoint

class TeensyException(Exception):
    pass


class Teensy:
    def __init__(
        self,
        vid: int = 0x16C0,
        pid: int = 0x0483,
        baudrate: int = 115200,
        crc: bool = True,
    ):
        self._teensy = None
        self.crc = crc
        self._crc8 = crc8.crc8()
        self.last_message = None
        self.end_bytes = b"\xBA\xDD\x1C\xC5"
        self.l = Logger()

        for port in serial.tools.list_ports.comports():
            if port.vid == vid and port.pid == pid:
                self._teensy = serial.Serial(port.device, baudrate=baudrate)
                break
        if self._teensy == None:
            self.l.log("No Teensy found !", 3)
            #raise TeensyException("No Device !")
        self.messagetype = {}
        self._reciever = threading.Thread(
            target=self.__receiver__, name="TeensyReceiver"
        )
        #self._reciever.start()

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
                    self.l.log("Invalid CRC8, skipping message", 1)
                    self.send_bytes(b"\x7F")
                    self._crc8.reset()
                    continue
                self._crc8.reset()

            else:
                msg = msg[:-4]

            lenmsg = msg[-1]

            if lenmsg > len(msg):
                self.l.log(
                    "Received Teensy message that does not match declared length "
                    + msg.hex(sep=" "), 1
                )
                continue
            try:
                if msg[0] == 127:
                    self.l.log("Received a NACK")
                    if self.last_message != None:
                        self.send_bytes(self.last_message)
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
        self, vid: int = 5824, pid: int = 1155, baudrate: int = 115200, crc: bool = True
    ):
        super().__init__(vid, pid, baudrate, crc)
        # All position are in the form tuple(X, Y, THETA)
        self.odometrie = OrientedPoint(0.0, 0.0, 0.0)
        self.position_offset = OrientedPoint(0.0, 0.0, 0.0)
        self.action_finished = True
        """
        This is used to match a handling function to a message type.
        add_callback can also be used.
        """
        self.messagetype = {
            128: self.rcv_odometrie,  # \x80
            129: self.rcv_action_finish,  # \x45
            255: self.unknowed_msg,
        }

    #####################
    # Position handling #
    #####################
    @Logger
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

    def rcv_odometrie(self, msg: bytes):
        self.odometrie = OrientedPoint(
            struct.unpack("<f", msg[0:4])[0],
            struct.unpack("<f", msg[4:8])[0],
            struct.unpack("<f", msg[8:12])[0],
        )

    @Logger
    def rcv_action_finish(self, msg: bytes):
        self.l.log("Action finished : " + msg.hex())
        self.action_finished = True

    def unknowed_msg(self, msg: bytes):
        self.l.log(f"Teensy does not know the command {msg.hex()}")

    #########################
    # User facing functions #
    #########################

    class Command:
        GoToPoint = b"\x00"
        SetSpeed = b"\x01"
        KeepCurrentPosition = b"\02"
        DisablePid = b"\03"
        EnablePid = b"\04"
        ResetPosition = b"\05"
        Stop = b"\x7E"  # 7E = 126
        Invalid = b"\xFF"

    @Logger
    def Go_To(
        self,
        position: OrientedPoint,
        direction: bool = False,
        speed: bytes = b"\x64",
        next_position_delay: int = 100,
        action_error_auth: int = 20,
        traj_precision: int = 50,
    ) -> None:
        """
        Va à la position donnée en paramètre

        :param position: la position en X et Y (et theta)
        :type position: OrientedPoint
        :param direction: en avant (false) ou en arrière (true), defaults to False
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
        self.action_finished = False
        pos = self.true_pos(position)
        msg = (
            self.Command.GoToPoint
            + struct.pack("<f", pos.x)
            + struct.pack("<f", pos.y)
            + struct.pack("<?", direction)
            + speed
            + struct.pack("<H", next_position_delay)
            + struct.pack("<H", action_error_auth)
            + struct.pack("<H", traj_precision)
        )
        # https://docs.python.org/3/library/struct.html#format-characters
        self.send_bytes(msg)

    @Logger
    def curve_go_to(self, destination: list[float, float], center: list[float, float], interval: int, direction: bool = False, speed: bytes = b'\x64', next_position_delay: int = 100, action_error_auth: int = 20, traj_precision: int = 50) -> None:
        """Go to a point with a curve"""
        
        # center 
        center_pos = self.true_pos(center)

        # angle between the actual position and the destination
        angle_to_destination = math.atan2(destination[1] - center_pos[1], destination[0] - center_pos[0])

        # distance between the center and the destination (rayon)
        radius = math.sqrt((destination[0] - center_pos[0]) ** 2 + (destination[1] - center_pos[1]) ** 2)

        # chord length 
        chord_length = math.sqrt((destination[0] - center_pos[0]) ** 2 + (destination[1] - center_pos[1]) ** 2)
        
        #arc distance
        arc_length = radius * angle_to_destination

        #send specific commands with new arc_length
        curve_msg = (
        self.Command.GoToPoint +
        struct.pack("<ff", destination[0], destination[1]) +  # target_point
        struct.pack("<ff", center[0], center[1]) +  # center_point
        struct.pack("<H", interval) +  # interval
        struct.pack("<H", next_position_delay) +  # delay
        struct.pack("<?", direction) +  # direction
        speed +  # speed
        struct.pack("<H", traj_precision)
        )
        self.send_bytes(curve_msg)
        self.action_finished = True
    
    @Logger
    def Set_Speed(self, speed: float) -> None:
        self.action_finished = False
        msg = self.Command.GoToPoint + struct.pack(speed, "f")
        self.send_bytes(msg)

    @Logger
    def Keep_Current_Position(self):
        self.action_finished = False
        msg = self.Command.KeepCurrentPosition
        self.send_bytes(msg)

    @Logger
    def Disable_Pid(self):
        self.action_finished = False
        msg = self.Command.DisablePid
        self.send_bytes(msg)

    @Logger
    def Enable_Pid(self):
        self.action_finished = False
        msg = self.Command.EnablePid
        self.send_bytes(msg)

    @Logger
    def Set_Home(self):
        self.action_finished = False
        msg = self.Command.ResetPosition
        self.send_bytes(msg)

    @Logger
    def Stop(self):
        self.action_finished = False
        msg = self.Command.Stop
        self.send_bytes(msg)


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
