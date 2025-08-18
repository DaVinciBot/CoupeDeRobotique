"""Enums used across path planning components."""

from enum import Enum, auto


class PathPlanningStrategy(Enum):
    """Available algorithms for generating paths.

    Attributes:
        A_STAR: Use A* algorithm.
        BASIC: Use basic path finding algorithm: rotate face to target,
            move straight forward.
        DELTA: Do step replacement, no path finding -> rotate or move straight.

    """

    A_STAR = auto()
    """Use A* algorithm."""
    BASIC = auto()
    """Use basic path finding algo: rotate face to target, move straight forward."""
    DELTA = auto()
    """Do step replacement, no path finding -> rotate or move straight."""


class Direction(Enum):
    """Motion direction for a planned path.

    Attributes:
        FORWARD: Move forward.
        BACKWARD: Move backward.

    """

    FORWARD = auto()
    """Move forward."""
    BACKWARD = auto()
    """Move backward."""
