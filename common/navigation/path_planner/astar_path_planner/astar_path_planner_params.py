from navigation.path_planner.structs import PathFindingStrategy, Direction
from navigation.path_planner.base_path_planner.base_path_planner_params import BasePathPlannerParams


class AstarPathPlannerParams(BasePathPlannerParams):
    def __init__(
            self,
            resolution: int,
            smooth_trajectory: bool = True,
            backwards: Direction = Direction.FORWARD,
    ):
        self.resolution: int = resolution
        self.smooth_trajectory: bool = smooth_trajectory
        self.backwards: Direction = backwards
        super().__init__(PathFindingStrategy.A_STAR)
