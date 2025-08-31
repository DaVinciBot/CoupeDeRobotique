"""Enumeration of all events used in the navigation system."""

from __future__ import annotations

from enum import Enum, auto


class NavigatorSignalsEnum(Enum):
    """Enumeration of all events used in the navigation system.

    These events represent key actions or statuses relevant to path planning,
    trajectory execution, obstacle handling, goal processing, and system diagnostics.

    Attributes:
        PLAN_PATH: Initiate path planning.
        PATH_PLANNED: Path planning completed successfully.
        PLAN_TRAJECTORY: Initiate trajectory planning.
        TRAJECTORY_PLANNED: Trajectory planning completed successfully.
        REPLAN_PATH: Replan the path due to changes or obstacles.
        START_MOTION: Start motion along the planned trajectory.
        PAUSE_MOTION: Pause the current motion.
        RESUME_MOTION: Resume the paused motion.
        STOP_MOTION: Stop the current motion immediately.
        ERROR_MOTION: An error occurred during motion execution.
        ACS: Anti-collision system triggered.
        OBSTACLE_DETECTED: An obstacle has been detected.
        GOAL_REACHED: The target goal has been reached.
        GOAL_NOT_REACHABLE: The target goal is determined to be unreachable.
        NAVIGATOR_ERROR: A system error has occurred.
        NAVIGATOR_READY: The navigator is ready for operation.

    """

    # ===== Path and Trajectory Planning =====
    PLAN_PATH = auto()
    """Initiate path planning"""
    PATH_PLANNED = auto()
    """Path planning completed successfully"""
    PLAN_TRAJECTORY = auto()
    """Initiate trajectory planning"""
    TRAJECTORY_PLANNED = auto()
    """Trajectory planning completed successfully"""
    REPLAN_PATH = auto()
    """Replan the path due to changes or obstacles"""

    # ===== Motion Control =====
    START_MOTION = auto()
    """Start motion along the planned trajectory"""
    PAUSE_MOTION = auto()
    """Pause the current motion"""
    RESUME_MOTION = auto()
    """Resume the paused motion"""
    STOP_MOTION = auto()
    """Stop the current motion immediately"""
    ERROR_MOTION = auto()
    """An error occurred during motion execution"""

    # ===== Obstacle and Collision Handling =====
    ACS = auto()
    """Anti-collision system triggered"""
    OBSTACLE_DETECTED = auto()
    """An obstacle has been detected"""

    # ===== Goal Management =====
    GOAL_REACHED = auto()
    """The target goal has been reached"""
    GOAL_NOT_REACHABLE = auto()
    """The target goal is determined to be unreachable"""

    # ===== System Status =====
    NAVIGATOR_ERROR = auto()
    """A system error has occurred"""
    NAVIGATOR_READY = auto()
    """The navigator is ready for operation"""
