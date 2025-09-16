"""Enumeration of supported actuator types for Teensy GPIO pins."""

from __future__ import annotations

from enum import Enum, auto


class ActuatorType(Enum):
    """Enum representing different types of actuators.

    Attributes:
        UNKNOWN: Default undefined actuator type.
        SERVO: Represents a servo motor.
        STEPPER: Represents a stepper motor.
        LCD: Represents an LCD-display.
    """

    UNKNOWN = auto()
    """Default undefined actuator type."""
    SERVO = auto()
    """Represents a servo motor."""
    STEPPER = auto()
    """Represents a stepper motor."""
    LCD = auto()
    """Represents an LCD-display."""
