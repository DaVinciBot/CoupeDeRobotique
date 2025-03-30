from enum import Enum, auto


class PathFindingStrategy(Enum):
    A_STAR = auto()  # Use A* algorithm
    BASIC = auto()  # Use basic path finding algorithm: rotate face to target, move straight forward
    DUMMY = auto()  # Do step replacement, no path finding -> rotate or move straight


class Direction(Enum):
    FORWARD = auto()
    BACKWARD = auto()
