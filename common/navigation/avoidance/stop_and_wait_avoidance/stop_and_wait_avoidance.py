# ====== Code Summary ======
# This module defines a StopAndWaitAvoidance class, implementing a stop-and-wait strategy
# for obstacle avoidance in a robotic navigation system.
# The strategy halts movement upon obstacle detection (via ACS),
# waits until the obstacle is cleared or a timeout occurs,
# and then either replans the path or aborts the operation.
# The system uses zones and trajectory commands to update navigation behavior.

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


class StopAndWaitAvoidance(BaseAvoidance[StopAndWaitAvoidanceParams]):
    """
    Implements a stop-and-wait obstacle avoidance strategy:

    When an obstacle is detected via ACS (Automatic Collision System), the robot stops.
    If the obstacle is cleared, it replans a path starting from the current position.
    If a timeout occurs before clearance, the system aborts avoidance with a stop command.

    Attributes:
        params (StopAndWaitAvoidanceParams): Parameters for stop-and-wait strategy.
        logger (Logger | None): Optional logger for debug output.
    """

    def __init__(
        self,
        params: StopAndWaitAvoidanceParams,
        logger: Logger | None = None,
    ) -> None:
        """
        Initialize the StopAndWaitAvoidance with parameters and optional logger.

        Args:
            params (StopAndWaitAvoidanceParams): Configuration parameters.
            logger (Logger | None): Optional logging instance.
        """
        super().__init__(params, logger)

    @BaseAvoidance._ensure_original_task_storage
    def handle(
        self,
        task: "NavigatorTask",
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

        # 1. Timeout check
        if self._has_timed_out():
            return self._abort(task, position)

        # 2. Obstacle detected: begin avoidance
        if self._acs(ally_zone, enemy_zone) and self.state == AvoidanceState.IDLE:
            # Stop the robot and initiate avoidance procedure
            cmd = TrajectoryPlanCommand.create_stop_command(current_position=position)
            task.current_trajectory_command = cmd
            self.state = AvoidanceState.AVOIDING
            task.state = NavigatorTaskState.AVOIDING
            self._start_timer()
            return cmd

        # 3. Obstacle cleared: finish avoidance
        if self.state == AvoidanceState.AVOIDING and not self._acs(
            ally_zone, enemy_zone
        ):
            # Obstacle is no longer detected, replan from current position
            last_params = task.path_planner.last_plan_path_params
            last_params.start = position  # Update start position to current location
            new_path = task.path_planner.plan_path(last_params)
            task.trajectory_planner.plan_trajectory(new_path)
            task.trajectory_planner.start_planning()  # Reset internal clock

            self._reset_timer()
            self.state = AvoidanceState.IDLE
            task.state = NavigatorTaskState.IN_PROGRESS
            return (
                task.current_trajectory_command
            )  # Not important, this will be ignored because the avoidance is over

        # 4. Continue with original trajectory
        # No changes, continue executing the existing trajectory command
        return task.current_trajectory_command
