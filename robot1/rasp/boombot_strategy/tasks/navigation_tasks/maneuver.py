from config_loader import CONFIG

from navigation import (
    NoAvoidanceParams,
    DeltaPathPlannerParams,
    SequentialTrajectoryPlannerParams,
    Direction,
)

from boombot_strategy.tasks.navigation_tasks.navigation_task import NavigationTask


class Backward(NavigationTask):
    def __init__(self, distance: float):
        super().__init__(
            goal=None,
            path_planner_params=DeltaPathPlannerParams(distance=-distance),
            trajectory_planner_params=SequentialTrajectoryPlannerParams(
                direction=Direction.BACKWARD
            ),
            speed_profiler=CONFIG.ROLLING_BASIS_DEFAULT_SPEED_PROFILER,
            avoidance_params=NoAvoidanceParams(),
        )


class PreciseForward(NavigationTask):
    def __init__(self, distance: float):
        super().__init__(
            goal=None,
            path_planner_params=DeltaPathPlannerParams(distance=distance),
            trajectory_planner_params=SequentialTrajectoryPlannerParams(),
            speed_profiler=CONFIG.ROLLING_BASIS_SLOW_SPEED_PROFILER,
            avoidance_params=NoAvoidanceParams(),
        )
