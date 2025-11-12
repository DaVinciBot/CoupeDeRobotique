"""Backward obstacle avoidance strategy."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from navigation.avoidance.acs_detection_profiles.no_acs_detection_profile import (
    NoAcsDetectionProfileParams,
)
from navigation.avoidance.back_avoidance.back_avoidance_params import (
    BackAvoidanceParams,
)
from navigation.avoidance.base_avoidance import AvoidanceState, BaseAvoidance
from navigation.avoidance.no_avoidance import NoAvoidanceParams
from navigation.navigator.task import (
    NavigatorTask,
    NavigatorTaskParams,
    NavigatorTaskState,
)
from navigation.path_planner import Direction
from navigation.path_planner.delta_path_planner import DeltaPathPlannerParams
from navigation.trajectory_planner.sequential_trajectory_planner import (
    SequentialTrajectoryPlannerParams,
)

if TYPE_CHECKING:
    from loggerplusplus import Logger

    from arena.base_arena.arena_zones import AllyZone, EnemyZone
    from geometry import OrientedPoint
    from navigation.avoidance.acs_detection_profiles.base_acs_detection_profiles import (  # noqa: E501
        BaseAcsDetectionProfileParams,
    )
    from navigation.path_planner.base_path_planner import BasePathPlannerPlanPathParams
    from navigation.trajectory_planner import TrajectoryPlanCommand


class BackAvoidance(BaseAvoidance[BackAvoidanceParams]):
    """Implement a simple backward obstacle avoidance strategy.

    When an obstacle is detected via ACS the robot moves backward for a configured
    distance. If the obstacle disappears before the timeout expires, a new path
    is planned from the current position. When the timeout is reached, the
    avoidance is aborted.
    """

    def __init__(
        self,
        params: BackAvoidanceParams,
        acs_detection_profile_params: BaseAcsDetectionProfileParams,
        logger: Logger | None = None,
    ) -> None:
        """Initialize the avoidance with parameters and optional logger.

        Args:
            params (BackAvoidanceParams): Configuration parameters.
            acs_detection_profile_params (BaseAcsDetectionProfileParams):
                Parameters for ACS detection profile.
            logger (Logger | None, optional):
                Logger instance for debugging. Defaults to None.
        """
        super().__init__(params, acs_detection_profile_params, logger)

        self.state: AvoidanceState = AvoidanceState.IDLE
        self.backward_navigator_task: NavigatorTask | None = None

    @BaseAvoidance.ensure_original_task_storage
    def handle(
        self,
        current_navigator_task: NavigatorTask,
        ally_zone: AllyZone,
        enemy_zone: EnemyZone,
    ) -> TrajectoryPlanCommand:
        """Process avoidance logic based on current zones and navigation state.

        Args:
            current_navigator_task (NavigatorTask):
                The current navigation task instance.
            ally_zone (AllyZone): Ally zone providing positional data.
            enemy_zone (EnemyZone): Enemy zone used for obstacle detection.

        Returns:
            TrajectoryPlanCommand:
            The trajectory command after processing avoidance logic.
        """
        position: OrientedPoint = ally_zone.point
        self._logger.debug(
            f"[NAV:Avoid] Handling at pos: {position}, state: {self.state}",
        )

        # 1. Timeout check
        if self._has_timed_out():
            self._logger.warning("[NAV:Avoid] Timeout reached - aborting task")
            return self._abort(current_navigator_task, position)

        # 2. Obstacle detected → init backward task
        if (
            self.acs_detector.is_acs_triggered(ally_zone, enemy_zone)
            and self.state == AvoidanceState.IDLE
        ):
            self._logger.info(
                "[NAV:Avoid] Obstacle detected at "
                f"{ally_zone.point.distance(enemy_zone.point):.1f}cm - "
                "initiating backward avoidance",
            )

            # Create backward navigator task
            self.backward_navigator_task = NavigatorTask(
                NavigatorTaskParams(
                    goal=None,
                    timeout=None,
                    stabilization_delay=0.0,
                    path_planner_params=DeltaPathPlannerParams(
                        distance=self.params.backward_distance,
                    ),
                    trajectory_planner_params=SequentialTrajectoryPlannerParams(
                        direction=Direction.BACKWARD,
                    ),
                    speed_profiler=self.params.backward_speed_profiler,
                    avoidance_params=NoAvoidanceParams(),
                    acs_detection_profile_params=NoAcsDetectionProfileParams(),
                ),
            )

            self.state = AvoidanceState.AVOIDING
            current_navigator_task.state = NavigatorTaskState.AVOIDING
            self._start_timer()
            self._logger.debug(
                f"[NAV:Avoid] Timer started at: {self._avoiding_start_time}",
            )

            # Execute first backward command immediately
            cmd = self.backward_navigator_task.handle(ally_zone, enemy_zone)
            current_navigator_task.current_trajectory_command = cmd
            return cmd

        # 3. While avoiding → keep executing backward
        if (
            self.state == AvoidanceState.AVOIDING
            and self.backward_navigator_task is not None
        ):
            self._logger.debug("[NAV:Avoid] Executing backward maneuver")
            cmd: TrajectoryPlanCommand = self.backward_navigator_task.handle(
                ally_zone,
                enemy_zone,
            )

            # Clear the backward task if it has finished
            if self.backward_navigator_task.state == NavigatorTaskState.FINISHED:
                self.backward_navigator_task = None

            current_navigator_task.current_trajectory_command = cmd
            return cmd  # Return the command from the backward avoidance task

        # 4. Finished backward, obstacle clear → replan
        if (
            self.state == AvoidanceState.AVOIDING
            and self.backward_navigator_task is None
        ):
            self._logger.info("[NAV:Avoid] Obstacle cleared - replanning trajectory")

            # Obstacle is no longer detected, replan from current position
            last_params = cast(
                "BasePathPlannerPlanPathParams",
                current_navigator_task.path_planner.last_plan_path_params,
            )
            last_params.start = position  # Update start position to current location

            self._logger.debug(f"[NAV:Avoid] Replanning from: {position}")

            new_path = current_navigator_task.path_planner.plan_path(last_params)
            current_navigator_task.trajectory_planner.plan_trajectory(new_path)
            current_navigator_task.trajectory_planner.start_planning()

            self._logger.debug("[NAV:Avoid] Trajectory planner clock reset")
            # reset timer just for logging/manure measurement
            self._reset_timer()
            self._logger.debug("[NAV:Avoid] Timer reset")

            self.state = AvoidanceState.IDLE
            current_navigator_task.state = NavigatorTaskState.IN_PROGRESS

            self._logger.info("[NAV:Avoid] Complete - resuming normal operation")
            return cast(
                "TrajectoryPlanCommand",
                current_navigator_task.current_trajectory_command,
            )  # Avoidance complete, continue as normal

        # 4. Continue with current command
        self._logger.debug("[NAV:Avoid] No action required - continuing trajectory")
        return cast(
            "TrajectoryPlanCommand",
            current_navigator_task.current_trajectory_command,
        )
