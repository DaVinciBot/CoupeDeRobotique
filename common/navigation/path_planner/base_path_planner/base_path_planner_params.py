from navigation.path_planner.structs import PathFindingStrategy, Direction


class BasePathPlannerParams:
    def __init__(
            self, path_finding_strategy: PathFindingStrategy
    ):
        self.path_finding_strategy: PathFindingStrategy = path_finding_strategy
