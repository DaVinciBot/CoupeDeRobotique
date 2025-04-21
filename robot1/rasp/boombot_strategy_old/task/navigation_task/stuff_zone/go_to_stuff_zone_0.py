from navigation import (
    BaseAvoidanceParams,
    BaseTrajectoryPlannerParams,
    BasePathPlannerParams,
    SpeedProfiler,
)


from boombot_strategy.task.navigation_task.navigation_task import NavigationTask


class GoToStuffZone0(NavigationTask):
    def __init__(
        self,
        path_planner_params: BasePathPlannerParams,
        trajectory_planner_params: BaseTrajectoryPlannerParams,
        speed_profiler: SpeedProfiler,
        avoidance_params: BaseAvoidanceParams,
        timeout: float | None = None,
    ):
        super().__init__(
            goal=0,
            timeout=timeout,
            path_planner_params=path_planner_params,
            trajectory_planner_params=trajectory_planner_params,
            speed_profiler=speed_profiler,
            avoidance_params=avoidance_params,
        )
