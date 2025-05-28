# ====== Standard Library Imports ======
from __future__ import annotations
from typing import TYPE_CHECKING
import math

# ====== Internal Project Imports ======
from arena import AllyZone, EnemyZone
from geometry import OrientedPoint
from loggerplusplus import Logger
from navigation.avoidance.base_avoidance import BaseAvoidance
from navigation.avoidance.base_avoidance.states import AvoidanceState
from navigation.avoidance.back_avoidance.back_avoidance_params import (
    BackAvoidanceParams,
)
from navigation.trajectory_planner import TrajectoryPlanCommand
from navigation.avoidance.acs_detection_profiles import BaseAcsDetectionProfileParams

if TYPE_CHECKING:
    from navigation.navigator.task.navigator_task import NavigatorTask


class BackAvoidance(BaseAvoidance[BackAvoidanceParams]):
    """
    Implements a back obstacle avoidance strategy.

    When an obstacle is detected via ACS, the robot reverses by a configured distance.
    If the obstacle clears during the reverse phase before a timeout, it replans a new trajectory.
    If the timeout expires at any phase, the avoidance aborts.

    Attributes:
        params (BackAvoidanceParams): Parameters for the strategy.
        acs_detection_profile_params (BaseAcsDetectionProfileParams): Parameters for ACS detection profile.
        logger (Logger | None): Optional logger.
    """

    def __init__(
        self,
        params: BackAvoidanceParams,
        acs_detection_profile_params: BaseAcsDetectionProfileParams,
        logger: Logger | None = None,
    ) -> None:
        """
        Initialize the BackAndForwardAvoidance with parameters and optional logger.

        Args:
            params (BackAndForwardAvoidanceParams): Configuration parameters.
            acs_detection_profile_params (BaseAcsDetectionProfileParams): Parameters for ACS detection profile.
            logger (Logger | None): Optional logging instance.
        """
        super().__init__(params, acs_detection_profile_params, logger)

    @BaseAvoidance._ensure_original_task_storage
    def handle(
        self,
        current_navigator_task: NavigatorTask,
        ally_zone: AllyZone,
        enemy_zone: EnemyZone,
    ) -> TrajectoryPlanCommand:
        """
        Main handler to process avoidance logic based on current zones and navigation state.

        Args:
            current_navigator_task (NavigatorTask): The current navigation task instance.
            ally_zone (AllyZone): Ally zone providing positional data.
            enemy_zone (EnemyZone): Enemy zone used for obstacle detection.

        Returns:
            TrajectoryPlanCommand: The trajectory command after processing avoidance logic.
        """
        from navigation.navigator.task.states import NavigatorTaskState

        position: OrientedPoint = ally_zone.point
        self.logger.debug(
            f"Handling avoidance at position: {position}, current state: {self.state}"
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
                f"Distance: {ally_zone.point.distance(enemy_zone.point)}"
            )

            th_distance: float = self.params.backward_distance

            th_x = ally_zone.point.x - th_distance * math.cos(ally_zone.point.theta)
            th_y = ally_zone.point.y - th_distance * math.sin(ally_zone.point.theta)

            cmd = TrajectoryPlanCommand(
                position=OrientedPoint(th_x, th_y, ally_zone.point.theta),
                linear_speed=self.params.backward_speed,
                angular_speed=0.0,
            )

            current_navigator_task.current_trajectory_command = cmd
            self.state = AvoidanceState.AVOIDING
            current_navigator_task.state = NavigatorTaskState.AVOIDING
            self._start_timer()
            self.logger.debug(f"Timer started at: {self._avoiding_start_time}")
            return cmd

        # 3. Continue with current command
        self.logger.debug(
            "No avoidance action required. Continuing original trajectory."
        )
        return current_navigator_task.current_trajectory_command
