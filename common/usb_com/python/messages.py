"""Message identifiers and constants for Teensy USB communication."""

from __future__ import annotations

from enum import Enum

# This signature must be exactly the same on both sides (Raspberry Pi and Teensy)
# to ensure valid communication.
END_BYTES_SIGNATURE: bytes = b"\xba\xdd\x1c\xc5"


class Messages(Enum):
    r"""Enumeration for command types exchanged between the Raspberry Pi and Teensy.

    Commands from Raspberry Pi to Teensy are in the range ``0``-``127`` while
    those from Teensy to Raspberry Pi are in ``128``-``255``.

    Attributes:
        SET_TARGET_POSITION: Command to set the rolling basis target position.
        SET_PID: Update PID coefficients for the rolling basis.
        SET_ODOMETRIE: Reset the odometry.
        SET_SERVO_ANGLE_I2C: Set a servo angle over I\ :sub:``2``\ C.
        STEPPER_STEP: Move a stepper motor.
        SET_SERVO_ANGLE_DETACH: Move a servo then detach it.
        ATTACH_SWITCH: Attach a switch on the actuators board.
        SET_SERVO_ANGLE: Set a servo angle.
        SET_STEPPER_DRIVER_ACTIVATION_STATE: Enable or disable the stepper driver.
        RESET_TEENSY: Reset the Teensy board.
        NACK: Notification of an invalid command.
        UPDATE_ROLLING_BASIS: Send odometry data from the Teensy.
        SWITCH_STATE_RETURN: Report the state of a switch.
        PRINT: Print a message from the Teensy.
        UNKNOWN_MSG_TYPE: Unknown command identifier.
    """

    # rasp -> teensy : 0-127 (Convention)

    # Rolling Basis
    SET_TARGET_POSITION = 0
    """Command to set the rolling basis target position."""
    SET_PID = 1
    """Update PID coefficients for the rolling basis."""
    SET_ODOMETRIE = 2
    """Reset the odometry."""

    # Actuators
    SET_SERVO_ANGLE_I2C = 3
    """Set a servo angle over I2C."""
    STEPPER_STEP = 4
    """Move a stepper motor."""
    SET_SERVO_ANGLE_DETACH = 5
    """Move a servo then detach it."""
    ATTACH_SWITCH = 6
    """Attach a switch on the actuators board."""
    SET_SERVO_ANGLE = 7
    """Set a servo angle."""
    SET_STEPPER_DRIVER_ACTIVATION_STATE = 8
    """Enable or disable the stepper driver."""

    # Common (Rolling Basis + Actuators)
    RESET_TEENSY = 126
    """Reset the Teensy board."""

    # two ways : 127 (Convention)
    NACK = 127
    """Notification of an invalid command."""

    # teensy -> rasp : 128-255 (Convention)
    # Rolling Basis
    UPDATE_ROLLING_BASIS = 128
    """Send odometry data from the Teensy."""

    # Actuators
    SWITCH_STATE_RETURN = 129
    """Report the state of a switch."""

    # Common (Rolling Basis + Actuators)
    PRINT = 254
    """Print a message from the Teensy."""
    UNKNOWN_MSG_TYPE = 255
    """Unknown command identifier."""

    # To use for message creation
    def to_bytes(self) -> bytes:
        """Converts the command to its byte representation.

        Returns:
            bytes: Single-byte representation of the command.
        """
        return bytes([self.value])
