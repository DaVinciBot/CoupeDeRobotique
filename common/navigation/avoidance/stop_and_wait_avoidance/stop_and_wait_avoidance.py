"""Stop-and-wait obstacle avoidance strategy."""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    cast,
)

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
    from navigation.path_planner.base_path_planner import BasePathPlannerPlanPathParams


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
        self.logger.debug(
            f"Handling avoidance at position: {position}, current state: {self.state}",
        )

        # 1. Timeout check
        if self._has_timed_out():
            self.logger.warning("Avoidance timed out. Aborting task.")
            return self._abort(current_navigator_task, position)

        # 2. Obstacle detected: begin avoidance
        if (
            self.acs_detector.is_acs_triggered(ally_zone, enemy_zone)
            and self.state == AvoidanceState.IDLE
        ):
            self.logger.info(
                f"Obstacle detected. Stopping robot and initiating avoidance. "
                f"Distance: {ally_zone.point.distance(enemy_zone.point)}",
            )

            # Stop the robot and initiate avoidance procedure
            cmd = TrajectoryPlanCommand.create_stop_command(current_position=position)
            current_navigator_task.current_trajectory_command = cmd
            self.state = AvoidanceState.AVOIDING
            current_navigator_task.state = NavigatorTaskState.AVOIDING
            self._start_timer()
            self.logger.debug(f"Timer started at: {self._avoiding_start_time}")
            return cmd

        # 3. Obstacle cleared: finish avoidance
        if (
            self.state == AvoidanceState.AVOIDING
            and not self.acs_detector.is_acs_triggered(ally_zone, enemy_zone)
        ):
            self.logger.info("Obstacle cleared. Replanning trajectory.")

            # Obstacle is no longer detected, replan from current position
            last_params = cast(
                "BasePathPlannerPlanPathParams",
                current_navigator_task.path_planner.last_plan_path_params,
            )
            last_params.start = position

            self.logger.debug(f"Replanning from updated start: {position}")

            new_path = current_navigator_task.path_planner.plan_path(last_params)
            current_navigator_task.trajectory_planner.plan_trajectory(new_path)
            current_navigator_task.trajectory_planner.start_planning()

            self.logger.debug("Trajectory planner reset internal clock.")
            self._reset_timer()
            self.logger.debug("Timer reset after avoidance completion.")

            self.state = AvoidanceState.IDLE
            current_navigator_task.state = NavigatorTaskState.IN_PROGRESS

            self.logger.info("Avoidance complete. Resuming normal operation.")
            return cast(
                "TrajectoryPlanCommand",
                current_navigator_task.current_trajectory_command,
            )  # Avoidance complete, continue as normal

        # 4. Continue with original trajectory
        self.logger.debug(
            "No avoidance action required. Continuing original trajectory.",
        )
        return cast(
            "TrajectoryPlanCommand",
            current_navigator_task.current_trajectory_command,
        )
