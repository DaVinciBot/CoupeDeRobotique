# ====== Code Summary ======
# This module defines the `BasicPathPlannerParams` class, a parameter configuration specifically for the
# `BasicPathPlanner`. It extends the base class to include a direction attribute that determines whether
# the generated path should be FORWARD or BACKWARD, and sets the pathfinding strategy to BASIC.

from geometry import OrientedPoint
from navigation.path_planner.base_path_planner.base_path_planner_params import (
    BasePathPlannerParams,
    BasePathPlannerPlanPathParams,
)
from navigation.path_planner.structs import Direction, PathPlanningStrategy


class BasicPathPlannerParams(BasePathPlannerParams):
    """Parameter class for the BasicPathPlanner.

    Attributes:
        direction (Direction): Indicates whether the path should be planned FORWARD or BACKWARD.
    """

    def __init__(self, direction: Direction = Direction.FORWARD) -> None:
        """Initialize parameters for the basic path planner.

        Args:
            direction (Direction): Direction of motion (default is FORWARD).
        """
        self.direction: Direction = direction
        super().__init__(PathPlanningStrategy.BASIC)


class BasicPathPlannerPlanPathParams(BasePathPlannerPlanPathParams):
    def __init__(self, start: OrientedPoint, goal: OrientedPoint) -> None:
        self.goal: OrientedPoint = goal
        super().__init__(start)
