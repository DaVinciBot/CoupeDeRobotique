# ====== Code Summary ======
# This module defines `DeltaPathPlannerParams`, a configuration class for the `DeltaPathPlanner`.
# It inherits from `BasePathPlannerParams` and initializes its strategy as DELTA.

from geometry import OrientedPoint
from navigation.path_planner.base_path_planner.base_path_planner_params import (
    BasePathPlannerParams,
    BasePathPlannerPlanPathParams,
)
from navigation.path_planner.structs import PathPlanningStrategy


class DeltaPathPlannerParams(BasePathPlannerParams):
    """Parameter class for DeltaPathPlanner.

    Initializes the path finding strategy as DELTA.
    """

    def __init__(self, distance: float = 0.0, rotation: float = 0.0) -> None:
        """Initialize delta-based path planner parameters with DELTA strategy.

        Args:
            distance (float, optional): Distance to travel. Defaults to 0.0.
            rotation (float, optional): Rotation to apply. Defaults to 0.0.
        """
        self.distance: float = distance
        self.rotation: float = rotation
        super().__init__(PathPlanningStrategy.DELTA)


class DeltaPathPlannerPlanPathParams(BasePathPlannerPlanPathParams):
    """Parameters for the delta path planner."""

    def __init__(self, start: OrientedPoint) -> None:
        """Initialize parameters for the delta path planner.

        Args:
            start (OrientedPoint): Starting point of the path.
        """
        super().__init__(start)
