"""Base parameters for trajectory planners."""

from navigation.path_planner import Direction
from navigation.trajectory_planner.structs import TrajectoryPlannerStrategy


class BaseTrajectoryPlannerParams:
    """Base class for trajectory planner parameter configurations."""

    def __init__(
        self,
        trajectory_planning_strategy: TrajectoryPlannerStrategy,
        direction: Direction,
    ) -> None:
        """Initialize the base planner parameters.

        Args:
            trajectory_planning_strategy (TrajectoryPlannerStrategy):
                The strategy used for generating trajectories.
            direction (Direction): The direction of the trajectory.

        """
        self.trajectory_planning_strategy: TrajectoryPlannerStrategy = (
            trajectory_planning_strategy
        )
        self.direction: Direction = direction
