"""Tasks that drive the robot to a goal using planning components."""

from __future__ import annotations

from typing import TYPE_CHECKING

from navigation.navigator.task import NavigatorTask, NavigatorTaskParams
from strategy.core.base_game_context import BaseGameContext
from strategy.core.tasks.base_task import BaseTask

if TYPE_CHECKING:
    from loggerplusplus import Logger

    from arena.base_arena.arena_zones import BaseArenaZone
    from geometry import OrientedPoint
    from navigation.avoidance.acs_detection_profiles.base_acs_detection_profiles import (  # noqa: E501
        BaseAcsDetectionProfileParams,
    )
    from navigation.avoidance.base_avoidance import BaseAvoidanceParams
    from navigation.path_planner.base_path_planner import BasePathPlannerParams
    from navigation.trajectory_planner.base_trajectory_planner import (
        BaseTrajectoryPlannerParams,
    )
    from navigation.trajectory_planner.speed_profile import SpeedProfiler


class BaseNavigationTask[GameContextT: BaseGameContext](BaseTask[GameContextT]):
    """Common functionality for tasks that navigate through the arena."""

    def __init__(
        self,
        goal: int | BaseArenaZone | OrientedPoint | None,
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
            goal (int | BaseArenaZone | OrientedPoint | None):
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

        self.goal: int | BaseArenaZone | OrientedPoint | None = goal
        self.stabilization_delay: float = stabilization_delay
        self.timeout: float | None = timeout
        self.path_planner_params = path_planner_params
        self.trajectory_planner_params = trajectory_planner_params
        self.speed_profiler = speed_profiler
        self.avoidance_params = avoidance_params
        self.acs_detection_profile_params = acs_detection_profile_params

        self._is_initialized: bool = False
        self.navigator_task: NavigatorTask

    def _initialize(self, ctx: GameContextT) -> None:
        """Initialize the navigation task.

        Args:
            ctx (GameContextT): The game context.
        """
        self._is_initialized = True

        if callable(self.goal):
            try:
                computed_goal = self.goal(ctx)
            except TypeError:
                computed_goal = self.goal()
        else:
            computed_goal = self.goal

        self.navigator_task = NavigatorTask(
            params=NavigatorTaskParams(
                goal=(
                    ctx.arena.compute_goal_position(computed_goal) if computed_goal else None),
                # goal can be None when we use DeltaPathPlanner
                timeout=self.timeout,
                path_planner_params=self.path_planner_params,
                trajectory_planner_params=self.trajectory_planner_params,
                speed_profiler=self.speed_profiler,
                avoidance_params=self.avoidance_params,
                acs_detection_profile_params=self.acs_detection_profile_params,
                stabilization_delay=self.stabilization_delay,
            ),
        )
