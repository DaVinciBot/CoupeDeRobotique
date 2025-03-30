# ====== Imports ======
# Internal project imports
from navigation.path_planner.structs import PathFindingStrategy, Direction
from navigation.path_planner.base_path_planner.base_path_planner_params import BasePathPlannerParams


# ====== Dummy Path Planner Params Class ======
class DummyPathPlannerParams(BasePathPlannerParams):
    def __init__(self):
        super().__init__(PathFindingStrategy.DUMMY)
