# ====== Imports ======
# Standard library imports
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

# Third-party imports
from loggerplusplus import Logger

# Local imports
from arena import AllyZone, EnemyZone
from geometry import OrientedPoint
import time

# Internal project imports
# - Avoidance
# Base
from navigation.avoidance.base_avoidance import BaseAvoidance, AvoidanceState

# Stop and Wait
from navigation.avoidance.stop_and_wait_avoidance.stop_and_wait_avoidance_params import StopAndWaitAvoidanceParams

# - Path Planner
from navigation.path_planner import BasePathPlannerPlanPathParams

# - Trajectory Planner
from navigation.trajectory_planner import TrajectoryPlanCommand

# - NavigatorTask
# TODO: trouver une solution pour cet import circulaire
# from navigation.navigator.task.states import NavigatorTaskState
from enum import Enum, auto


class NavigatorTaskState(Enum):
    NOT_PLANNED = auto()
    IN_PROGRESS = auto()
    AVOIDING = auto()
    ABORT = auto()


# ====== Base Avoidance Class ======
class StopAndWaitAvoidance(BaseAvoidance[StopAndWaitAvoidanceParams]):

    def __init__(
            self,
            params: StopAndWaitAvoidanceParams,
            logger: Logger | None = None
    ) -> None:
        super().__init__(params, logger)

        self._avoiding_start_time: float = 0.0

    @BaseAvoidance._ensure_original_task_storage
    def handle(
            self,
            current_navigator_task: 'NavigatorTask',
            ally_zone: AllyZone, enemy_zone: EnemyZone
    ) -> 'NavigatorTask':
        # Check if avoidance timeout is reached
        if self._avoiding_start_time != 0.0 and time.time() - self._avoiding_start_time > self.params.timeout:
            self.state = AvoidanceState.ABORTED
            current_navigator_task.state = NavigatorTaskState.AVOIDING
            current_navigator_task.current_trajectory_plan_command = TrajectoryPlanCommand.create_stop_command(
                current_position=ally_zone.point,
            )
            return current_navigator_task

        # If ACS triggerd: start the avoidance strategy: stop and wait
        if self._acs(ally_zone, enemy_zone):
            if self.state == AvoidanceState.IDLE:
                current_navigator_task.current_trajectory_plan_command = TrajectoryPlanCommand.create_stop_command(
                    current_position=ally_zone.point,
                )
                self._avoiding_start_time = time.time()
                self.state = AvoidanceState.AVOIDING
                current_navigator_task.state = NavigatorTaskState.AVOIDING

        elif self.state == AvoidanceState.AVOIDING:
            # If the avoidance is finished, restore the original task
            # We have to re-plan the trajectory because we didn't have the current theorical speed

            # Get last plan path params
            last_plan_path: BasePathPlannerPlanPathParams = current_navigator_task.path_planner.last_plan_path_params

            # Keep all params except start that we need to change
            last_plan_path.start = ally_zone.point

            # Re-plan the path
            new_path: list[OrientedPoint] = current_navigator_task.path_planner.plan_path(
                last_plan_path
            )

            # Re-plan the trajectory
            current_navigator_task.trajectory_planner.plan_trajectory(new_path)

            self._avoiding_start_time: float = 0.0
            self.state = AvoidanceState.IDLE
            current_navigator_task.state = NavigatorTaskState.IN_PROGRESS

        return current_navigator_task
