# ====== Code Summary ======
# This module defines ``SequentialTrajectoryPlannerParams``, a configuration class for the
# SequentialTrajectoryPlanner. It extends the base parameter class and introduces a configurable
# sleep delay between each trajectory step.

from navigation.path_planner import Direction
from navigation.trajectory_planner.base_trajectory_planner.base_trajectory_planner_params import (
    BaseTrajectoryPlannerParams,
)
from navigation.trajectory_planner.structs import TrajectoryPlannerStrategy


class SequentialTrajectoryPlannerParams(BaseTrajectoryPlannerParams):
    """Parameter class for SequentialTrajectoryPlanner."""

    def __init__(
        self,
        direction: Direction = Direction.FORWARD,
        step_sleep_delay: float = 0.0,
        respect_intermediate_orientation: bool = False,
        respect_goal_orientation: bool = True,
    ) -> None:
        """Initialize parameters for sequential trajectory planning.

        Args:
            direction (Direction, optional): Direction in which to generate the trajectory.
                Defaults to Direction.FORWARD.
            step_sleep_delay (float, optional): Time delay between each segment in the trajectory.
                Defaults to 0.0.
            respect_intermediate_orientation (bool, optional): Whether intermediate poses
                should preserve their orientation when planning the trajectory. Defaults to ``False``.
            respect_goal_orientation (bool, optional): Whether the final pose orientation
                should be preserved. Defaults to ``True``.

        """
        self.step_sleep_delay: float = step_sleep_delay
        self.respect_intermediate_orientation: bool = respect_intermediate_orientation
        self.respect_goal_orientation: bool = respect_goal_orientation
        super().__init__(
            trajectory_planning_strategy=TrajectoryPlannerStrategy.SEQUENTIAL,
            direction=direction,
        )
