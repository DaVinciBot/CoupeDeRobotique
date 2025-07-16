from enum import Enum, auto


class AvoidanceState(Enum):
    """Enum representing the state of the avoidance process.
    """

    IDLE = auto()  # No avoidance in progress
    AVOIDING = auto()  # Avoidance in progress
    ABORTED = auto()  # Avoidance aborted, multiple reasons: error, timeout, etc.
