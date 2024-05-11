from enum import Enum


class AntiCollisionMode(Enum):
    # No anti-collision not implemented
    DISABLED = 0
    # Stop when an obstacle is detected not implemented
    CIRCULAR = 1
    # Stop when an obstacle is detected in front of the robot not implemented
    FRONTAL = 2
    # Mode to use lidar with its cap (doesn't check behind him but can detect obstacles on the side)
    SEMI_CIRCULAR = 3


class AntiCollisionHandle(Enum):
    DO_NOTHING = 0
    WAIT_AND_FAIL = 1
    WAIT_AND_RETRY = 2
    AVOID = 3
