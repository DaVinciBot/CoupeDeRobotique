"""Parameters for basic trajectory planner."""

from __future__ import annotations

from navigation.path_planner import Direction
from navigation.trajectory_planner.base_trajectory_planner import (
    BaseTrajectoryPlannerParams,
)
from navigation.trajectory_planner.structs import TrajectoryPlannerStrategy


class BasicTrajectoryPlannerParams(BaseTrajectoryPlannerParams):
    """Configuration parameters for basic trajectory planner.

    The basic trajectory planner creates curved trajectories by detecting when
    consecutive segments can be smoothly connected.
    """

    def __init__(
        self,
        direction: Direction = Direction.FORWARD,
        curve_detection_angle_threshold: float = 0.5,
        curve_smoothness: float = 0.3,
        *,
        respect_goal_orientation: bool = True,
    ) -> None:
        """Initialize basic trajectory planner parameters.

        Args:
            direction (Direction, optional):
                The direction of the trajectory. Defaults to Direction.FORWARD.
            curve_detection_angle_threshold (float, optional):
                Maximum angle change (in radians) between segments to be considered
                for curve smoothing. Defaults to 0.5 (~28 degrees).
            curve_smoothness (float, optional):
                Smoothing factor for curves, range [0, 1]. Higher values create
                smoother curves. Defaults to 0.3.
            respect_goal_orientation (bool, optional):
                If True, ensures final orientation matches goal. Defaults to True.
        """
        self.curve_detection_angle_threshold = curve_detection_angle_threshold
        self.curve_smoothness = curve_smoothness
        self.respect_goal_orientation = respect_goal_orientation
        super().__init__(
            trajectory_planning_strategy=TrajectoryPlannerStrategy.BASIC,
            direction=direction,
        )
