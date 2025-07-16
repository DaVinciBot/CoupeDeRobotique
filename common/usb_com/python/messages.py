# ====== Code Summary ======
# This module defines an enumeration (Messages) representing command types exchanged
# between a Raspberry Pi and a Teensy microcontroller over USB communication.
# Commands are categorized based on direction (Raspberry Pi -> Teensy: 0-127, Teensy -> Raspberry Pi: 128-255).
# The module also includes a signature constant used for USB communication integrity.

from enum import Enum

# This signature must be exactly the same on both sides (Raspberry Pi and Teensy) to ensure valid communication.
END_BYTES_SIGNATURE: bytes = b"\xba\xdd\x1c\xc5"


class Messages(Enum):
    """Enumeration for command types exchanged between the Raspberry Pi and Teensy.

    Commands from Raspberry Pi to Teensy are in the range 0-127,
    while those from Teensy to Raspberry Pi are in the range 128-255.
    """

    # rasp -> teensy : 0-127 (Convention)

    # Rolling Basis
    SET_TARGET_POSITION = 0
    SET_PID = 1
    SET_ODOMETRIE = 2

    # Actuators
    SET_SERVO_ANGLE_I2C = 3
    STEPPER_STEP = 4
    SET_SERVO_ANGLE_DETACH = 5
    ATTACH_SWITCH = 6
    SET_SERVO_ANGLE = 7
    SET_STEPPER_DRIVER_ACTIVATION_STATE = 8

    # Common (Rolling Basis + Actuators)
    RESET_TEENSY = 126

    # two ways : 127 (Convention)
    NACK = 127

    # teensy -> rasp : 128-255 (Convention)
    # Rolling Basis
    UPDATE_ROLLING_BASIS = 128

    # Actuators
    SWITCH_STATE_RETURN = 129

    # Common (Rolling Basis + Actuators)
    PRINT = 254
    UNKNOWN_MSG_TYPE = 255

    # To use for message creation
    def to_bytes(self) -> bytes:
        """Converts the command to its byte representation.

        Returns:
            bytes: Single-byte representation of the command.
        """
        return bytes([self.value])
