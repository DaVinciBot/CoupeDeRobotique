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
from navigation.avoidance.acs_detection_profiles import (
    BaseAcsDetectionProfile,
    BaseAcsDetectionProfileParams,
)

from loggerplusplus import Logger


class BaseNavigationTask(BaseTask):
    def __init__(
        self,
        goal: int | BaseArenaZone | OrientedPoint | Point | None,
        path_planner_params: BasePathPlannerParams,
        trajectory_planner_params: BaseTrajectoryPlannerParams,
        speed_profiler: SpeedProfiler,
        avoidance_params: BaseAvoidanceParams,
        acs_detection_profile_params: BaseAcsDetectionProfileParams,
        stabilization_delay: float,  # in seconds
        timeout: float | None = None,  # in seconds, None means no timeout
        logger: Logger | None = None,
    ):
        super().__init__(logger=logger)

        self.goal: int | BaseArenaZone | OrientedPoint | Point | None = goal
        self.stabilization_delay: float = (
            stabilization_delay * 1000
        )  # Convert to milliseconds
        self.timeout: float | None = (
            timeout * 1000 if timeout is not None else None
        )  # Convert to milliseconds
        self.path_planner_params = path_planner_params
        self.trajectory_planner_params = trajectory_planner_params
        self.speed_profiler = speed_profiler
        self.avoidance_params = avoidance_params
        self.acs_detection_profile_params = acs_detection_profile_params

        self._is_initialized: bool = False
        self.navigator_task: NavigatorTask | None = None

    def _initialize(self, ctx: BaseGameContext) -> None:
        self._is_initialized = True

        self.navigator_task: NavigatorTask = NavigatorTask(
            params=NavigatorTaskParams(
                goal=(
                    ctx.arena.compute_goal_position(self.goal) if self.goal else None
                ),  # goal can be None when we use DeltaPathPlanner
                timeout=self.timeout,
                path_planner_params=self.path_planner_params,
                trajectory_planner_params=self.trajectory_planner_params,
                speed_profiler=self.speed_profiler,
                avoidance_params=self.avoidance_params,
                acs_detection_profile_params=self.acs_detection_profile_params,
                stabilization_delay=self.stabilization_delay,
            )
        )

    @abstractmethod
    def handle(self, ctx: BaseGameContext) -> bool: ...
