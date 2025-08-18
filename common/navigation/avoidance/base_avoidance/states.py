"""Enumeration describing avoidance states."""

from enum import Enum, auto


class AvoidanceState(Enum):
    """State of the avoidance process.

    Attributes:
        IDLE: No avoidance in progress.
        AVOIDING: Avoidance in progress.
        ABORTED: Avoidance aborted: error, timeout, etc.

    """

    IDLE = auto()
    """No avoidance in progress"""
    AVOIDING = auto()
    """Avoidance in progress"""
    ABORTED = auto()
    """Avoidance aborted: error, timeout, etc."""
