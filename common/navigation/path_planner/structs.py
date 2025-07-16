# ====== Code Summary ======
# This module defines two enumerations used in path planning: `PathFindingStrategy` and `Direction`.
# `PathFindingStrategy` specifies the algorithmic strategy for generating paths.
# `Direction` indicates the intended direction of movement (FORWARD or BACKWARD).

from enum import Enum, auto


class PathPlanningStrategy(Enum):
    """Enumeration of available path finding strategies."""

    A_STAR = auto()  # Use A* algorithm
    BASIC = (
        auto()
    )  # Use basic path finding algorithm: rotate face to target, move straight forward
    DELTA = auto()  # Do step replacement, no path finding -> rotate or move straight


class Direction(Enum):
    """Enumeration of motion directions for path planners."""

    FORWARD = auto()
    BACKWARD = auto()
