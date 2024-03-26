from config_loader import CONFIG
from logger import Logger, LogLevels

# Import from common
from teensy_comms import Teensy

import struct


class Actuators(Teensy):
    name = "actuators"

    def __init__(
        self,
        logger: Logger,
        ser=12678600,  # T1
        vid: int = 5824,
        pid: int = 1155,
        baudrate: int = 115200,
        crc: bool = True,
        pin_servos_left: list[int] = CONFIG.GOD_HAND_GRAB_SERVO_PINS_LEFT,
        pin_servos_right: list[int] = CONFIG.GOD_HAND_GRAB_SERVO_PINS_RIGHT,
        pin_deployment: int = CONFIG.GOD_HAND_DEPLOYMENT_SERVO_PIN,
    ):
        super().__init__(logger, ser, vid, pid, baudrate, crc)
        self.pin_servos_left = pin_servos_left
        self.pin_servos_right = pin_servos_right

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
            self.l.log(
                f"you tried to write {angle}° on pin {pin} whereas angle must be between {min_angle} and {max_angle}°",
                LogLevels.ERROR,
            )
