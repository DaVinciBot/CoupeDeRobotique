from config_loader import CONFIG

from boombot_strategy.tasks.navigation_tasks import NavigationTask
from navigation import (
    StopAndWaitAvoidanceParams,
    BasicPathPlannerParams,
    SequentialTrajectoryPlannerParams,
    Direction,
)


class GoToColorReservedZoneToFinishGame(NavigationTask):
    def __init__(self, color_reserved_zone_id: int):
        super().__init__(
            goal=color_reserved_zone_id,
            path_planner_params=BasicPathPlannerParams(),
            trajectory_planner_params=SequentialTrajectoryPlannerParams(),
            speed_profiler=CONFIG.ROLLING_BASIS_HIGH_SPEED_PROFILER,  # Be fast to finish the game
            avoidance_params=StopAndWaitAvoidanceParams(timeout=10),
            acs_detection_profile_params=CONFIG.ACS_PROFILE_GO_TO_COLOR_RESERVED_ZONE_TO_FINISH_GAME,
        )


class GoToColorReservedZoneToConstruct(NavigationTask):
    def __init__(self, color_reserved_zone_id: int):
        super().__init__(
            goal=color_reserved_zone_id,
            path_planner_params=BasicPathPlannerParams(),
            trajectory_planner_params=SequentialTrajectoryPlannerParams(),
            speed_profiler=CONFIG.ROLLING_BASIS_TO_CONSTRUCT_SPEED_PROFILER,  # Be careful to construct
            avoidance_params=StopAndWaitAvoidanceParams(timeout=10),
            acs_detection_profile_params=CONFIG.ACS_PROFILE_GO_TO_COLOR_RESERVED_ZONE_TO_CONSTRUCT,
        )
