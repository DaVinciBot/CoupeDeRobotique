from config_loader import CONFIG

from boombot_strategy.task.navigation_task import NavigationTask
from navigation import (
    StopAndWaitAvoidanceParams,
    DeltaPathPlannerParams,
    SequentialTrajectoryPlannerParams,
)


class BackwardToQuitConstruction(NavigationTask):
    def __init__(self):
        super().__init__(
            goal=None,
            path_planner_params=DeltaPathPlannerParams(distance=-10),
            trajectory_planner_params=SequentialTrajectoryPlannerParams(),
            speed_profiler=CONFIG.ROLLING_BASIS_HIGH_SPEED_PROFILER,  # Be fast to finish the game
            avoidance_params=StopAndWaitAvoidanceParams(acs_distance=50, timeout=10),
        )
