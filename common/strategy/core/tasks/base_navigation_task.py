"""Tasks that drive the robot to a goal using planning components."""

from __future__ import annotations

from typing import TYPE_CHECKING

from navigation.navigator.task import NavigatorTask, NavigatorTaskParams
from navigation.navigator.task.navigator_task_params import (
    DEFAULT_ANGLE_REACHED_TOLERANCE_RAD,
    DEFAULT_POSITION_REACHED_TOLERANCE_CM,
)
from strategy.core.base_game_context import BaseGameContext
from strategy.core.tasks.base_task import BaseTask

if TYPE_CHECKING:
    from collections.abc import Callable

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
        points: int = 0,
        estimated_duration: float | Callable[[GameContextT], float] = 0.0,
        position_reached_tolerance_cm: float = DEFAULT_POSITION_REACHED_TOLERANCE_CM,
        angle_reached_tolerance_rad: float = DEFAULT_ANGLE_REACHED_TOLERANCE_RAD,
        finish_after_expected_end_delay_s: float | None = None,
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
            points (int, optional):
                Points awarded for completing this task. Defaults to 0.
            estimated_duration (float | Callable[[GameContextT], float], optional):
                Estimated duration of the task in seconds. Defaults to 0.0.
            position_reached_tolerance_cm (float, optional):
                Accepted position error before considering the goal reached.
            angle_reached_tolerance_rad (float, optional):
                Accepted orientation error before considering the goal reached.
            finish_after_expected_end_delay_s (float | None, optional):
                Extra time after the planned trajectory duration before considering
                the task finished even if the goal is not reached.
        """
        super().__init__(
            logger=logger,
            points=points,
            estimated_duration=estimated_duration,
        )

        self.goal: int | BaseArenaZone | OrientedPoint | None = goal
        self.stabilization_delay: float = stabilization_delay
        self.timeout: float | None = timeout
        self.path_planner_params = path_planner_params
        self.trajectory_planner_params = trajectory_planner_params
        self.speed_profiler = speed_profiler
        self.avoidance_params = avoidance_params
        self.acs_detection_profile_params = acs_detection_profile_params
        self.position_reached_tolerance_cm = position_reached_tolerance_cm
        self.angle_reached_tolerance_rad = angle_reached_tolerance_rad
        self.finish_after_expected_end_delay_s = finish_after_expected_end_delay_s

        self._is_initialized: bool = False
        self.navigator_task: NavigatorTask

    def _initialize(self, ctx: GameContextT) -> None:
        """Initialize the navigation task.

        Args:
            ctx (GameContextT): The game context.
        """
        self._is_initialized = True

        self.navigator_task = NavigatorTask(
            params=NavigatorTaskParams(
                goal=(
                    ctx.arena.compute_goal_position(self.goal) if self.goal else None
                ),  # goal can be None when we use DeltaPathPlanner
                timeout=self.timeout,
                position_reached_tolerance_cm=self.position_reached_tolerance_cm,
                angle_reached_tolerance_rad=self.angle_reached_tolerance_rad,
                finish_after_expected_end_delay_s=(
                    self.finish_after_expected_end_delay_s
                ),
                path_planner_params=self.path_planner_params,
                trajectory_planner_params=self.trajectory_planner_params,
                speed_profiler=self.speed_profiler,
                avoidance_params=self.avoidance_params,
                acs_detection_profile_params=self.acs_detection_profile_params,
                stabilization_delay=self.stabilization_delay,
            ),
        )
