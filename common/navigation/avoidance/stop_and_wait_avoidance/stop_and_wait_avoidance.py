# ====== Code Summary ======
# This module defines the StopAndWaitAvoidance class, which implements a stop-and-wait strategy
# for obstacle avoidance in a robotic navigation system. When an obstacle is detected using ACS,
# the robot halts and waits for the obstacle to clear or a timeout to occur. Upon clearance,
# it replans the path; if a timeout happens first, it aborts and issues a stop command.

# ====== Standard Library Imports ======
from __future__ import annotations
from typing import TYPE_CHECKING

# ====== Internal Project Imports ======
from arena import AllyZone, EnemyZone
from geometry import OrientedPoint
from loggerplusplus import Logger
from navigation.avoidance.base_avoidance import BaseAvoidance
from navigation.avoidance.base_avoidance.states import AvoidanceState
from navigation.avoidance.stop_and_wait_avoidance.stop_and_wait_avoidance_params import (
    StopAndWaitAvoidanceParams,
)
from navigation.trajectory_planner import TrajectoryPlanCommand

from navigation.avoidance.acs_detection_profiles import (
    BaseAcsDetectionProfileParams,
)

if TYPE_CHECKING:
    from navigation.navigator.task.navigator_task import NavigatorTask


class StopAndWaitAvoidance(BaseAvoidance[StopAndWaitAvoidanceParams]):
    """
    Implements a stop-and-wait obstacle avoidance strategy.

    When an obstacle is detected via ACS (Automatic Collision System), the robot stops.
    If the obstacle clears before a timeout, it replans a new trajectory from its current position.
    If the obstacle remains and a timeout occurs, the system aborts the avoidance process.

    Attributes:
        params (StopAndWaitAvoidanceParams): Parameters for stop-and-wait strategy.
        logger (Logger | None): Optional logger for debug output.
    """

    def __init__(
        self,
        params: StopAndWaitAvoidanceParams,
        acs_detection_profile_params: BaseAcsDetectionProfileParams,
        logger: Logger | None = None,
    ) -> None:
        """
        Initialize the StopAndWaitAvoidance with parameters and optional logger.

        Args:
            params (StopAndWaitAvoidanceParams): Configuration parameters.
            logger (Logger | None): Optional logging instance.
        """
        super().__init__(params, acs_detection_profile_params, logger)

    @BaseAvoidance._ensure_original_task_storage
    def handle(
        self,
        task: NavigatorTask,
        ally_zone: AllyZone,
        enemy_zone: EnemyZone,
    ) -> TrajectoryPlanCommand:
        """
        Main handler to process avoidance logic based on current zones and navigation state.

        Args:
            task (NavigatorTask): The current navigation task instance.
            ally_zone (AllyZone): Ally zone providing positional data.
            enemy_zone (EnemyZone): Enemy zone used for obstacle detection.

        Returns:
            TrajectoryPlanCommand: The trajectory command after processing avoidance logic.
        """
        from navigation.navigator.task.states import NavigatorTaskState

        position: OrientedPoint = ally_zone.point
        self.logger.debug(f"Handling avoidance at position: {position}, current state: {self.state}")

        # 1. Timeout check
        if self._has_timed_out():
            self.logger.warning("Avoidance timed out. Aborting task.")
            return self._abort(task, position)

        # 2. Obstacle detected: begin avoidance
        if (
            self.acs_detector.is_acs_triggered(ally_zone, enemy_zone)
            and self.state == AvoidanceState.IDLE
        ):
            self.logger.info(f"Obstacle detected. Stopping robot and initiating avoidance. "
                             f"Distance: {ally_zone.point.distance(enemy_zone.point)}")

            # Stop the robot and initiate avoidance procedure
            cmd = TrajectoryPlanCommand.create_stop_command(current_position=position)
            task.current_trajectory_command = cmd
            self.state = AvoidanceState.AVOIDING
            task.state = NavigatorTaskState.AVOIDING
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
            last_params = task.path_planner.last_plan_path_params
            last_params.start = position  # Update start position to current location

            self.logger.debug(f"Replanning from updated start: {position}")

            new_path = task.path_planner.plan_path(last_params)
            task.trajectory_planner.plan_trajectory(new_path)
            task.trajectory_planner.start_planning()  # Reset internal clock

            self.logger.debug("Trajectory planner reset internal clock.")
            self._reset_timer()
            self.logger.debug("Timer reset after avoidance completion.")

            self.state = AvoidanceState.IDLE
            task.state = NavigatorTaskState.IN_PROGRESS

            self.logger.info("Avoidance complete. Resuming normal operation.")
            return (
                task.current_trajectory_command
            )  # Avoidance complete, continue as normal

        # 4. Continue with original trajectory
        self.logger.debug("No avoidance action required. Continuing original trajectory.")
        return task.current_trajectory_command
