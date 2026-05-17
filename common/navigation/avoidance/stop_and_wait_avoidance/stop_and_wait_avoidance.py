"""Stop-and-wait obstacle avoidance strategy."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from navigation.avoidance.base_avoidance import AvoidanceState, BaseAvoidance
from navigation.avoidance.stop_and_wait_avoidance.stop_and_wait_avoidance_params import (  # noqa: E501
    StopAndWaitAvoidanceParams,
)
from navigation.navigator.task.states import NavigatorTaskState
from navigation.trajectory_planner import TrajectoryPlanCommand

if TYPE_CHECKING:
    from loggerplusplus import Logger

    from arena.base_arena.arena_zones import AllyZone, EnemyZone
    from geometry import OrientedPoint
    from navigation.avoidance.acs_detection_profiles.base_acs_detection_profiles.base_acs_detection_profiles_params import (  # noqa: E501
        BaseAcsDetectionProfileParams,
    )
    from navigation.navigator.task import NavigatorTask


class StopAndWaitAvoidance(BaseAvoidance[StopAndWaitAvoidanceParams]):
    """Implements a stop-and-wait obstacle avoidance strategy.

    When an obstacle is detected the robot stops. If the obstacle clears before
    a timeout, it replans a trajectory from its current position. Otherwise the
    avoidance procedure is aborted.
    """

    def __init__(
        self,
        params: StopAndWaitAvoidanceParams,
        acs_detection_profile_params: BaseAcsDetectionProfileParams,
        logger: Logger | None = None,
    ) -> None:
        """Initialize the stop-and-wait avoidance class.

        Args:
            params (StopAndWaitAvoidanceParams): Parameters for the avoidance strategy.
            acs_detection_profile_params (BaseAcsDetectionProfileParams):
                Parameters for the ACS detection profile.
            logger (Logger | None, optional): Logger instance for debugging.
                Defaults to ``None``.
        """
        super().__init__(params, acs_detection_profile_params, logger)
        self.state: AvoidanceState = AvoidanceState.IDLE

    @BaseAvoidance.ensure_original_task_storage
    def handle(
        self,
        current_navigator_task: NavigatorTask,
        ally_zone: AllyZone,
        enemy_zone: EnemyZone,
    ) -> TrajectoryPlanCommand:
        """Handle the stop-and-wait avoidance logic.

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
            f"[NAV:Avoid] Handling avoidance at pos: {position}, state: {self.state}",
        )

        # 1. Timeout check
        if self._has_timed_out():
            self._logger.warning("[NAV:Avoid] Timeout reached - aborting task")
            return self._abort(current_navigator_task, position)

        is_obstacle_detected = self.acs_detector.is_acs_triggered(
            ally_zone,
            enemy_zone,
        )

        # 2. Obstacle detected: begin avoidance
        if is_obstacle_detected and self.state == AvoidanceState.IDLE:
            distance = ally_zone.point.distance(enemy_zone.point)
            self._logger.warning(
                f"[NAV:Avoid] Obstacle detected at {distance:.1f}cm - stopping robot",
            )

            # Stop the robot and initiate avoidance procedure
            cmd = TrajectoryPlanCommand.create_stop_command(current_position=position)
            current_navigator_task.current_trajectory_command = cmd
            self.state = AvoidanceState.AVOIDING
            current_navigator_task.state = NavigatorTaskState.AVOIDING
            self._start_timer()
            return cmd

        if is_obstacle_detected and self.state == AvoidanceState.AVOIDING:
            self._logger.debug("[NAV:Avoid] Obstacle still present - keeping stop")
            cmd = TrajectoryPlanCommand.create_stop_command(current_position=position)
            current_navigator_task.current_trajectory_command = cmd
            return cmd

        # 3. Obstacle cleared: finish avoidance
        if self.state == AvoidanceState.AVOIDING:
            self._logger.info("[NAV:Avoid] Obstacle cleared - replanning trajectory")

            self._logger.debug(f"[NAV:Avoid] Replanning from updated start: {position}")

            cmd = (
                current_navigator_task.start_replanned_trajectory_from_current_position(
                    position,
                )
            )

            self._reset_timer()

            self.state = AvoidanceState.IDLE

            self._logger.info("[NAV:Avoid] Resuming normal navigation")
            return cmd

        # 4. Continue with original trajectory
        return cast(
            "TrajectoryPlanCommand",
            current_navigator_task.current_trajectory_command,
        )
