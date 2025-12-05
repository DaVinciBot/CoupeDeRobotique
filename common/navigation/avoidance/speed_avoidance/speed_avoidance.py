"""Speed-based ACS avoidance strategy."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from navigation.avoidance.base_avoidance import AvoidanceState, BaseAvoidance
from navigation.avoidance.speed_avoidance.speed_avoidance_params import (
    SpeedAvoidanceParams,
)
from navigation.navigator.task.states import NavigatorTaskState
from navigation.trajectory_planner import TrajectoryPlanCommand

if TYPE_CHECKING:
    from loggerplusplus import Logger
    from arena.base_arena.arena_zones import AllyZone, EnemyZone
    from geometry import OrientedPoint
    from navigation.avoidance.acs_detection_profiles.base_acs_detection_profiles.base_acs_detection_profiles_params import (
        BaseAcsDetectionProfileParams,
    )
    from navigation.navigator.task import NavigatorTask


class SpeedAvoidance(BaseAvoidance[SpeedAvoidanceParams]):
    """
    Avoidance strategy using dynamic ACS detection & robot speed.

    When an obstacle is detected via ACS, the robot stops immediately. If the obstacle
    clears before a timeout, it replans a trajectory from its current position. Otherwise,
    the avoidance procedure is aborted.
    """

    def __init__(
        self,
        params: SpeedAvoidanceParams,
        acs_detection_profile_params: BaseAcsDetectionProfileParams,
        logger: Logger | None = None,
    ) -> None:
        self.state: AvoidanceState = AvoidanceState.IDLE
        super().__init__(params, acs_detection_profile_params, logger)

    @BaseAvoidance.ensure_original_task_storage
    def handle(
        self,
        current_navigator_task: NavigatorTask,
        ally_zone: AllyZone,
        enemy_zone: EnemyZone,
    ) -> TrajectoryPlanCommand:
        """Handle the speed-based avoidance logic.
        Args:
            current_navigator_task (NavigatorTask): The current navigation task.
            ally_zone (AllyZone): The ally zone information.
            enemy_zone (EnemyZone): The enemy zone information.
        Returns:
            TrajectoryPlanCommand: The trajectory command after avoidance handling.
        """
        position: OrientedPoint = ally_zone.point
        self._logger.debug(
            f"[NAV:Avoid] Handling at pos: {position}, state: {self.state}",
        )

        # 1. Timeout check
        if self._has_timed_out():
            self._logger.warning("[NAV:Avoid-Speed] Timeout — aborting")
            return self._abort(current_navigator_task, position)

        # 2. Is ACS triggered ?
        triggered = self.acs_detector.is_acs_triggered(ally_zone, enemy_zone)

        # 3. Obstacle detected: begin avoidance
        if triggered and self.state == AvoidanceState.IDLE:

            self._logger.warning("[NAV:Avoid-Speed] URGENT collision → STOP")
            cmd = TrajectoryPlanCommand.create_stop_command(position)
            current_navigator_task.current_trajectory_command = cmd
            current_navigator_task.state = NavigatorTaskState.AVOIDING
            self.state = AvoidanceState.AVOIDING

            self._start_timer()
            return cmd

        # 4. Obstacle cleared: finish avoidance
        if not triggered and self.state == AvoidanceState.AVOIDING:
            self._logger.info("[NAV:Avoid-Speed] Obstacle cleared — replanning path")

            last_params = cast(
                "BasePathPlannerPlanPathParams",
                current_navigator_task.path_planner.last_plan_path_params,
            )
            last_params.start = position

            self._logger.debug(f"[NAV:Avoid] Replanning from updated start: {position}")

            new_path = current_navigator_task.path_planner.plan_path(last_params)
            current_navigator_task.trajectory_planner.plan_trajectory(new_path)
            current_navigator_task.trajectory_planner.start_planning()

            self._reset_timer()

            self.state = AvoidanceState.IDLE
            current_navigator_task.state = NavigatorTaskState.IN_PROGRESS

            self._logger.info("[NAV:Avoid] Resuming normal navigation")
            return cast(
                "TrajectoryPlanCommand",
                current_navigator_task.current_trajectory_command,
            )  # Avoidance complete, continue as normal

        # 5. Continue with original trajectory
        return cast(
            "TrajectoryPlanCommand",
            current_navigator_task.current_trajectory_command,
        )
