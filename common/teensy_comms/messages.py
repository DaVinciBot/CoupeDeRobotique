from enum import Enum

class Messages(Enum):
    """
    Enumeration for command types exchanged between the Raspberry Pi and Teensy.

    Commands from Raspberry Pi to Teensy are in the range 0-127,
    while those from Teensy to Raspberry Pi are in the range 128-255.
    """
    # rasp -> teensy : 0-127 (Convention)
    
    # Rolling Basis
    SET_SPEED_AND_POSITION = 0
    SET_PID = 1
    SET_ODOMETRIE = 2

    # Actuators
    SET_SERVO_ANGLE = 3
    STEPPER_STEP = 4
    SET_SERVO_ANGLE_DETACH = 5
    ATTACH_SWITCH = 6

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
        """
        Converts the command to its byte representation.

        Returns:
            bytes: Single-byte representation of the command.
        """
        return bytes([self.value])