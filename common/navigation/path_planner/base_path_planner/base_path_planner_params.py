# ====== Code Summary ======
# This module defines `BasePathPlannerParams`, a base class for holding configuration parameters
# related to path planning. It primarily stores the pathfinding strategy to be used by the planner.

# ====== Internal Project Imports ======
from navigation.path_planner.structs import PathFindingStrategy, Direction


class BasePathPlannerParams:
    """
    Base class for path planner parameter configurations.

    Attributes:
        path_finding_strategy (PathFindingStrategy): The strategy used for generating paths.
    """

    def __init__(self, path_finding_strategy: PathFindingStrategy):
        """
        Initialize the base path planner parameters.

        Args:
            path_finding_strategy (PathFindingStrategy): Strategy for path finding.
        """
        self.path_finding_strategy: PathFindingStrategy = path_finding_strategy
