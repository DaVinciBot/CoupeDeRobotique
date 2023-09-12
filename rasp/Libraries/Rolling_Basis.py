from Teensy_UART import Teensy
import struct


class Rolling_basis(Teensy):
    ######################
    # Rolling basis init #
    ######################

    def __init__(self, vid: int = 5824, pid: int = 1155, baudrate: int = 115200):
        super().__init__(vid, pid, baudrate)
        self.action_finished = False
        """
        This is used to match a handling function to a message type.
        add_callback can also be used.
        """
        self.messagetype = {
            128: self.rcv_odometrie,  # \x80
            69: self.rcv_action_finish  # \x45
        }

    #############################
    # Received message handling #
    #############################

    def rcv_odometrie(self, msg: bytes):
        self.odometrie = [struct.unpack("<f", msg[0:4]),
                          struct.unpack("<f", msg[4:8]),
                          struct.unpack("<f", msg[8:12])]

    def rcv_action_finish(self, msg: bytes):
        self.action_finished = True

    #########################
    # User facing functions #
    #########################

    class Command:
        GoToPoint = b"\x00"
        SetSpeed = b"\x01"

    def Go_To(self, x: float, y: float, direction: bool = False, speed: bytes = b'\x64', next_position_delay: int = 100, action_error_auth: int = 20, traj_precision: int = 50) -> None:
        """Got to a point

        Args:
            x (float): x coordinate
            y (float): y coordinate
            direction (bool, optional): whether to go backwards or forwards. Defaults to False.
            next_position_delay (int, optional): _description_. Defaults to 100.
            action_error_auth (int, optional): _description_. Defaults to 20.
            traj_precision (int, optional): _description_. Defaults to 50.
        """
        msg = self.Command.GoToPoint + \
            struct.pack("<f", x) + \
            struct.pack("<f", y) + \
            struct.pack("<?", direction) + \
            speed + \
            struct.pack("<H", next_position_delay) + \
            struct.pack("<H", action_error_auth) + \
            struct.pack("<H", traj_precision)
        # https://docs.python.org/3/library/struct.html#format-characters

        self.send_bytes(msg)
        self.action_finished = True

    def Set_Speed(self, speed: float) -> None:
        msg = self.Command.GoToPoint + struct.pack(speed, "f")
        self.send_bytes(msg)
