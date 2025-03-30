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
from navigation.path_planner.basic_path_planner.basic_path_planner_params import BasicPathPlannerParams


# ====== Basic Path Planner Class ======
class BasicPathPlanner(BasePathPlanner[BasicPathPlannerParams]):

    def __init__(self, params: BasicPathPlannerParams, logger: Logger | None = None) -> None:
        super().__init__(params, logger)

    @staticmethod
    def _compute_backward_position(goal: OrientedPoint) -> OrientedPoint:
        return OrientedPoint(goal.x, goal.y, goal.theta + math.pi)

    def plan_path(self, start: OrientedPoint, goal: OrientedPoint) -> list[OrientedPoint]:
        return [
            start if self.params.direction == Direction.FORWARD else self._compute_backward_position(start),
            goal if self.params.direction == Direction.FORWARD else self._compute_backward_position(goal)
        ]
