# ====== Standard Library Imports ======
from enum import Enum, auto


# ====== Class Part ======
class ActuatorType(Enum):
    """
    Enum representing different types of actuators.

    Attributes:
        UNKNOWN: Default undefined actuator type.
        SERVO: Represents a servo motor.
        STEPPER: Represents a stepper motor.
        LCD: Represents an LCD-display.
    """
    UNKNOWN = auto()
    SERVO = auto()
    STEPPER = auto()
    LCD = auto()
