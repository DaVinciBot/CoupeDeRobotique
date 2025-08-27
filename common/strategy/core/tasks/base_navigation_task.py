"""Tasks that drive the robot to a goal using planning components."""

from loggerplusplus import Logger

from arena import BaseArenaZone
from geometry import OrientedPoint, Point
from navigation import (
    BaseAvoidanceParams,
    BasePathPlannerParams,
    BaseTrajectoryPlannerParams,
    NavigatorTask,
    NavigatorTaskParams,
    SpeedProfiler,
)
from navigation.avoidance.acs_detection_profiles import BaseAcsDetectionProfileParams
from strategy.core.base_game_context import BaseGameContext
from strategy.core.tasks.base_task import BaseTask


class BaseNavigationTask(BaseTask):
    """Common functionality for tasks that navigate through the arena."""

    def __init__(
        self,
        goal: int | BaseArenaZone | OrientedPoint | Point | None,
        path_planner_params: BasePathPlannerParams,
        trajectory_planner_params: BaseTrajectoryPlannerParams,
        speed_profiler: SpeedProfiler,
        avoidance_params: BaseAvoidanceParams,
        acs_detection_profile_params: BaseAcsDetectionProfileParams,
        stabilization_delay: float,
        timeout: float | None = None,
        logger: Logger | None = None,
    ) -> None:
        """Initializes the BaseNavigationTask with navigation and planning parameters.

        Args:
            goal (int | BaseArenaZone | OrientedPoint | Point | None):
                The navigation goal.
            path_planner_params (BasePathPlannerParams):
                Parameters for the path planner.
            trajectory_planner_params (BaseTrajectoryPlannerParams):
                Parameters for the trajectory planner.
            speed_profiler (SpeedProfiler): Speed profile manager.
            avoidance_params (BaseAvoidanceParams):
                Parameters for obstacle avoidance.
            acs_detection_profile_params (BaseAcsDetectionProfileParams):
                Parameters for ACS detection profile.
            stabilization_delay (float):
                Delay for stabilization after reaching the goal.
            timeout (float | None, optional):
                Timeout for the navigation task. Defaults to None.
            logger (Logger | None, optional):
                Logger instance for debugging. Defaults to None.

        """
        super().__init__(logger=logger)

        self.goal: int | BaseArenaZone | OrientedPoint | Point | None = goal
        self.stabilization_delay: float = stabilization_delay
        self.timeout: float | None = timeout
        self.path_planner_params = path_planner_params
        self.trajectory_planner_params = trajectory_planner_params
        self.speed_profiler = speed_profiler
        self.avoidance_params = avoidance_params
        self.acs_detection_profile_params = acs_detection_profile_params

        self._is_initialized: bool = False
        self.navigator_task: NavigatorTask | None = None

    def _initialize(self, ctx: BaseGameContext) -> None:
        """Initialize the navigation task.

        Args:
            ctx (BaseGameContext): The game context.

        """
        self._is_initialized = True

        self.navigator_task = NavigatorTask(
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
            ),
        )
