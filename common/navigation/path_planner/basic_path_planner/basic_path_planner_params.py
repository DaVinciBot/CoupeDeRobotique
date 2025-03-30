from navigation.path_planner.structs import PathFindingStrategy, Direction
from navigation.path_planner.base_path_planner.base_path_planner_params import BasePathPlannerParams


class BasicPathPlannerParams(BasePathPlannerParams):
    def __init__(
            self,
            direction: Direction = Direction.FORWARD,
    ):
        self.direction: Direction = direction
        super().__init__(PathFindingStrategy.BASIC)
