# ====== Code Summary ======
# This module defines `SequentialTrajectoryPlannerParams`, a configuration class for the
# SequentialTrajectoryPlanner. It extends the base parameter class and introduces a configurable
# sleep delay between each trajectory step.

# ====== Internal Project Imports ======
from navigation.trajectory_planner.base_trajectory_planner.base_trajectory_planner_params import (
    BaseTrajectoryPlannerParams,
)
from navigation.trajectory_planner.structs import TrajectoryPlannerStrategy


class SequentialTrajectoryPlannerParams(BaseTrajectoryPlannerParams):
    """
    Parameter class for SequentialTrajectoryPlanner.

    Attributes:
        step_sleep_delay (float): Optional delay (in seconds) to pause between trajectory steps.
    """

    def __init__(
        self,
        step_sleep_delay: float = 0.0,
        respect_intermediate_orientation: bool = False,
    ) -> None:
        """
        Initialize parameters for sequential trajectory planning.

        Args:
            step_sleep_delay (float): Time delay between each segment in the trajectory.
            respect_intermediate_orientation (bool): If True, the trajectory planner will
                respect the intermediate orientation of the robot when planning the trajectory.
        """
        self.step_sleep_delay: float = step_sleep_delay
        self.respect_intermediate_orientation: bool = respect_intermediate_orientation
        super().__init__(
            trajectory_planning_strategy=TrajectoryPlannerStrategy.SEQUENTIAL
        )
