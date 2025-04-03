# ====== Code Summary ======
# This module defines `SequentialTrajectoryPlannerParams`, a configuration class for the
# SequentialTrajectoryPlanner. It extends the base parameter class and introduces a configurable
# sleep delay between each trajectory step.

# ====== Internal Project Imports ======
from navigation.trajectory_planner.base_trajectory_planner.base_trajectory_planner_params import \
    BaseTrajectoryPlannerParams


class SequentialTrajectoryPlannerParams(BaseTrajectoryPlannerParams):
    """
    Parameter class for SequentialTrajectoryPlanner.

    Attributes:
        step_sleep_delay (float): Optional delay (in seconds) to pause between trajectory steps.
    """

    def __init__(self, step_sleep_delay: float = 0.0) -> None:
        """
        Initialize parameters for sequential trajectory planning.

        Args:
            step_sleep_delay (float): Time delay between each segment in the trajectory.
        """
        self.step_sleep_delay: float = step_sleep_delay
        super().__init__()
