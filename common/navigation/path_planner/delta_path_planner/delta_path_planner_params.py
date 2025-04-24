# ====== Code Summary ======
# This module defines `DeltaPathPlannerParams`, a configuration class for the `DeltaPathPlanner`.
# It inherits from `BasePathPlannerParams` and initializes its strategy as DELTA.

# ====== Imports ======
# Internal project imports
from navigation.path_planner.structs import PathPlanningStrategy, Direction
from navigation.path_planner.base_path_planner.base_path_planner_params import BasePathPlannerParams, \
    BasePathPlannerPlanPathParams
from geometry import OrientedPoint


class DeltaPathPlannerParams(BasePathPlannerParams):
    """
    Parameter class for DeltaPathPlanner.

    Initializes the path finding strategy as DELTA.
    """

    def __init__(self, distance: float = 0.0, rotation: float = 0.0):
        """
        Initialize delta-based path planner parameters with DELTA strategy.
        """
        self.distance: float = distance
        self.rotation: float = rotation
        super().__init__(PathPlanningStrategy.DELTA)


class DeltaPathPlannerPlanPathParams(BasePathPlannerPlanPathParams):

    def __init__(self, start: OrientedPoint):
        super().__init__(start)
