from navigation import (
    NavigatorTaskParams,
    NavigatorTask,
    TrajectoryPlanCommand,
    NavigatorState,
)
from strategy.core.tasks.base_task import BaseTask
from strategy.core.base_game_context import BaseGameContext
from abc import abstractmethod

from arena import BaseArenaZone
from geometry import OrientedPoint, Point

from navigation import (
    BaseAvoidanceParams,
    BaseTrajectoryPlannerParams,
    BasePathPlannerParams,
    SpeedProfiler,
)


class BaseNavigationTask(BaseTask):

    def __init__(
        self,
        goal: int | BaseArenaZone | OrientedPoint | Point | None,
        path_planner_params: BasePathPlannerParams,
        trajectory_planner_params: BaseTrajectoryPlannerParams,
        speed_profiler: SpeedProfiler,
        avoidance_params: BaseAvoidanceParams,
        timeout: float | None = None,
    ):
        self.goal: int | BaseArenaZone | OrientedPoint | Point | None = goal
        self.timeout: float | None = timeout
        self.path_planner_params = path_planner_params
        self.trajectory_planner_params = trajectory_planner_params
        self.speed_profiler = speed_profiler
        self.avoidance_params = avoidance_params

        self._is_initialized: bool = False
        self.navigator_task: NavigatorTask | None = None

    def _initialize(self, ctx: BaseGameContext) -> None:
        self._is_initialized = True

        self.navigator_task: NavigatorTask = NavigatorTask(
            params=NavigatorTaskParams(
                goal=ctx.arena.compute_goal_position(self.goal),
                timeout=self.timeout,
                path_planner_params=self.path_planner_params,
                trajectory_planner_params=self.trajectory_planner_params,
                speed_profiler=self.speed_profiler,
                avoidance_params=self.avoidance_params,
            )
        )

    @abstractmethod
    def handle(self, ctx: BaseGameContext) -> bool: ...
