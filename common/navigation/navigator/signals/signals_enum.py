# ====== Code Summary ======
# This module defines the NavigatorSignalsEnum enumeration, which categorizes and names
# all possible events that can occur within the navigation system. These events cover
# aspects such as path and trajectory planning, motion control, obstacle detection,
# goal management, and system status updates.

# ====== Standard Library Imports ======
from enum import Enum, auto


class NavigatorSignalsEnum(Enum):
    """
    Enumeration of all events used in the navigation system.

    These events represent key actions or statuses relevant to path planning,
    trajectory execution, obstacle handling, goal processing, and system diagnostics.
    """

    # ===== Path and Trajectory Planning =====
    PLAN_PATH = auto()  # Initiate path planning
    PATH_PLANNED = auto()  # Path planning completed successfully
    PLAN_TRAJECTORY = auto()  # Initiate trajectory planning
    TRAJECTORY_PLANNED = auto()  # Trajectory planning completed successfully
    REPLAN_PATH = auto()  # Replan the path due to changes or obstacles

    # ===== Motion Control =====
    START_MOTION = auto()  # Start motion along the planned trajectory
    PAUSE_MOTION = auto()  # Pause the current motion
    RESUME_MOTION = auto()  # Resume the paused motion
    STOP_MOTION = auto()  # Stop the current motion immediately
    ERROR_MOTION = auto()  # An error occurred during motion execution

    # ===== Obstacle and Collision Handling =====
    ACS = auto()  # Anti-collision system triggered
    OBSTACLE_DETECTED = auto()  # An obstacle has been detected

    # ===== Goal Management =====
    GOAL_REACHED = auto()  # The target goal has been reached
    GOAL_NOT_REACHABLE = auto()  # The target goal is determined to be unreachable

    # ===== System Status =====
    NAVIGATOR_ERROR = auto()  # A system error has occurred
    NAVIGATOR_READY = auto()  # The navigator is ready for operation
