from config_loader import CONFIG

from boombot_strategy.task.navigation_task import NavigationTask
from navigation import (
    StopAndWaitAvoidanceParams,
    BasicPathPlannerParams,
    SequentialTrajectoryPlannerParams,
)


class GoToStuffZoneToPickUp(NavigationTask):
    def __init__(self, stuff_zone_id: int):
        super().__init__(
            goal=stuff_zone_id,
            path_planner_params=BasicPathPlannerParams(),
            trajectory_planner_params=SequentialTrajectoryPlannerParams(),
            speed_profiler=CONFIG.ROLLING_BASIS_TO_PICKUP_SPEED_PROFILER,  # Use for pickup speed profiler
            avoidance_params=StopAndWaitAvoidanceParams(acs_distance=50, timeout=10),
        )
