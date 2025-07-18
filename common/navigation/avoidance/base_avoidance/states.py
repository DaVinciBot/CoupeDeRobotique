from enum import Enum, auto


class AvoidanceState(Enum):
    """State of the avoidance process.

    Attributes:
        IDLE: No avoidance is in progress.
        AVOIDING: The system is actively performing an avoidance maneuver.
        ABORTED: The avoidance was aborted (e.g. due to timeout).
    """

    IDLE = auto()  # No avoidance in progress
    AVOIDING = auto()  # Avoidance in progress
    ABORTED = auto()  # Avoidance aborted, multiple reasons: error, timeout, etc.
