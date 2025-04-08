# ====== Code Summary ======
# This module implements `AStarPathPlanner`, which returns a list of oriented points forming a path
# from start to goal. If the direction is set to BACKWARD, the planner adjusts the orientation of
# all points in the list by π radians to reflect the reverse motion requirement.

# ====== Imports ======
# Standard library imports
import math

# Third-party imports
from loggerplusplus import Logger

# Local imports
from geometry import OrientedPoint

# Internal project imports
from navigation.path_planner.structs import Direction
from navigation.path_planner.base_path_planner.base_path_planner import BasePathPlanner
from navigation.path_planner.astar_path_planner.astar_path_planner_params import (
    AStarPathPlannerParams, AStarPathPlannerPlanPathParams
)


class AStarPathPlanner(
    BasePathPlanner[AStarPathPlannerParams, AStarPathPlannerPlanPathParams]
):
    """
    A* path planner that generates a direct path between start and goal points using A* algorithm.
    If the direction is set to BACKWARD, the orientations are flipped by π radians.
    """

    def __init__(self, params: AStarPathPlannerParams, logger: Logger | None = None) -> None:
        """
        Initialize the A* path planner.

        Args:
            params (AStarPathPlannerParams): Parameters including motion direction.
            logger (Logger | None): Optional logger.
        """
        super().__init__(params, logger)

    @staticmethod
    def _compute_backward_position(goal: OrientedPoint) -> OrientedPoint:
        """
        Compute the backward-facing pose by flipping orientation by π.

        Args:
            goal (OrientedPoint): Original pose.

        Returns:
            OrientedPoint: Flipped pose for backward motion.
        """
        return OrientedPoint(goal.x, goal.y, goal.theta + math.pi)

    @BasePathPlanner._store_plan_path_params
    def plan_path(self, params: AStarPathPlannerPlanPathParams) -> list[OrientedPoint]:
        """
        Plan a list of Oriented points path from start to goal.

        Args:
            params (AStarPathPlannerPlanPathParams): Parameters including start and goal points.

        Returns:
            list[OrientedPoint]: List containing oriented path from the start to the goal,
            possibly reversed for backward direction.
        """
        start = params.start
        goal = params.goal

        path = []

        if path is None or len(path) == 0:
            self.logger.error("No path found.")
            return []

        if self.params.direction == Direction.BACKWARD:
            path = [self._compute_backward_position(point) for point in path]

        return path
