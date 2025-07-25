# ====== Code Summary ======
# This module defines the ``BasicPathPlannerParams`` class, a parameter configuration specifically for the
# ``BasicPathPlanner``. It extends the base class to include a direction attribute that determines whether
# the generated path should be FORWARD or BACKWARD, and sets the pathfinding strategy to BASIC.

from geometry import OrientedPoint
from navigation.path_planner.base_path_planner.base_path_planner_params import (
    BasePathPlannerParams,
    BasePathPlannerPlanPathParams,
)
from navigation.path_planner.structs import Direction, PathPlanningStrategy


class BasicPathPlannerParams(BasePathPlannerParams):
    """Parameter class for the BasicPathPlanner."""

    def __init__(self, direction: Direction = Direction.FORWARD) -> None:
        """Initialize parameters for the basic path planner.

        Args:
            direction (Direction, optional): Direction of motion. Defaults to Direction.FORWARD.
        """
        self.direction: Direction = direction
        super().__init__(PathPlanningStrategy.BASIC)


class BasicPathPlannerPlanPathParams(BasePathPlannerPlanPathParams):
    """Parameters for the basic path planner."""

    def __init__(self, start: OrientedPoint, goal: OrientedPoint) -> None:
        """Initialize parameters for the basic path planner.

        Args:
            start (OrientedPoint): Starting point of the path.
            goal (OrientedPoint): Goal point of the path.

        """
        self.goal: OrientedPoint = goal
        super().__init__(start)
