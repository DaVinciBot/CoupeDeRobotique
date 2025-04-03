# ====== Code Summary ======
# This module defines `DeltaPathPlannerParams`, a configuration class for the `DeltaPathPlanner`.
# It inherits from `BasePathPlannerParams` and initializes its strategy as DELTA.

# ====== Imports ======
# Internal project imports
from navigation.path_planner.structs import PathFindingStrategy, Direction
from navigation.path_planner.base_path_planner.base_path_planner_params import BasePathPlannerParams


class DeltaPathPlannerParams(BasePathPlannerParams):
    """
    Parameter class for DeltaPathPlanner.

    Initializes the path finding strategy as DELTA.
    """

    def __init__(self):
        """
        Initialize delta-based path planner parameters with DELTA strategy.
        """
        super().__init__(PathFindingStrategy.DELTA)
