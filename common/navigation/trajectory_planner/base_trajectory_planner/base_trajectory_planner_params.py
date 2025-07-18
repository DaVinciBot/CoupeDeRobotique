# ====== Code Summary ======
# This module defines a base class `BaseTrajectoryPlannerParams` intended to serve as a base for
# planner parameter configurations. The base implementation includes a no-op constructor.

from navigation.path_planner import Direction
from navigation.trajectory_planner.structs import TrajectoryPlannerStrategy


class BaseTrajectoryPlannerParams:
    """Base class for trajectory planner parameter configurations.

    Can be extended by specific planner parameter classes to include additional settings.
    """

    def __init__(
        self,
        trajectory_planning_strategy: TrajectoryPlannerStrategy,
        direction: Direction,
    ) -> None:
        """Initialize the base planner parameters.

        Args:
            trajectory_planning_strategy (TrajectoryPlannerStrategy): The strategy used for generating trajectories.
            direction (Direction): The direction of the trajectory.
        """
        self.trajectory_planning_strategy: TrajectoryPlannerStrategy = (
            trajectory_planning_strategy
        )
        self.direction: Direction = direction
