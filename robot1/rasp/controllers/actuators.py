from config_loader import CONFIG
from logger import Logger
# Import from common
from teensy_comms import Teensy

import struct


class Actuators(Teensy):
    name = "actuators"
    def __init__(
        self,
        ser=12678600, # T1
        vid: int = 5824,
        pid: int = 1155,
        baudrate: int = 115200,
        crc: bool = True,
        pin_servos: list[int] = CONFIG.SERVO_PINS,
        
    ):
        super().__init__(ser,vid, pid, baudrate, crc)
        self.pin_servos = pin_servos

    class Command:  # values must correspond to the one defined on the teensy
        ServoGoTo = b"\x01"

    def __str__(self) -> str:
        return self.__class__.__name__

    #########################
    # User facing functions #
    #########################

    @Logger
    def update_servo(
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
