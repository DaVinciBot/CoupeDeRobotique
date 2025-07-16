# ====== Code Summary ======
# This module defines `BasePathPlannerParams`, a base class for holding configuration parameters
# related to path planning. It primarily stores the pathfinding strategy to be used by the planner.

from geometry import OrientedPoint
from navigation.path_planner.structs import PathPlanningStrategy


class BasePathPlannerParams:
    """Base class for path planner parameter configurations.

    Attributes:
        path_finding_strategy (PathPlanningStrategy): The strategy used for generating paths.
    """

    def __init__(self, path_finding_strategy: PathPlanningStrategy):
        """Initialize the base path planner parameters.

        Args:
            path_finding_strategy (PathPlanningStrategy): Strategy for path finding.
        """
        self.path_finding_strategy: PathPlanningStrategy = path_finding_strategy


class BasePathPlannerPlanPathParams:
    def __init__(self, start: OrientedPoint):
        self.start: OrientedPoint = start
