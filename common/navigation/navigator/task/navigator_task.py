# ====== Code Summary ======
# This module defines the NavigatorTask class, which integrates a path planner, trajectory planner,
# and obstacle avoidance module based on provided configuration parameters. It supports strategy-based
# instantiation of specific planner implementations such as Delta and Basic for path planning,
# and Sequential for trajectory planning. Avoidance logic is instantiated as well but currently lacks
# extended strategy support.

# ====== Standard Library Imports ======
from typing import cast
import time

# ====== Third-Party Library Imports ======
# (None present)

# ====== Internal Project Imports ======
from navigation.path_planner import (
    # Strategy
    PathPlanningStrategy,
    # Base class
    BasePathPlanner,
    # Derivative classes
    DeltaPathPlanner,
    DeltaPathPlannerParams,
    DeltaPathPlannerPlanPathParams,
    BasicPathPlanner,
    BasicPathPlannerParams,
    BasicPathPlannerPlanPathParams,
)
from navigation.trajectory_planner import (
    # Strategy
    TrajectoryPlannerStrategy,
    # Base class
    BaseTrajectoryPlanner,
    # Derivative classes
    SequentialTrajectoryPlanner,
    SequentialTrajectoryPlannerParams,
)
from navigation.avoidance import (
    BaseAvoidance,
    AvoidanceStrategy,
    StopAndWaitAvoidance,
    StopAndWaitAvoidanceParams,
)

from navigation.navigator.task import NavigatorTaskParams

from arena import AllyZone, EnemyZone
from navigation.trajectory_planner import TrajectoryPlanCommand
from navigation.navigator.task.states import NavigatorTaskState

from navigation.path_planner import BasePathPlannerPlanPathParams
from geometry import OrientedPoint


from navigation.path_planner import PathPlannerFactory
from navigation.trajectory_planner import TrajectoryPlannerFactory
from navigation.avoidance import AvoidanceFactory


class NavigatorTask:
    """
    Manages the navigation task by composing path planning, trajectory planning, and avoidance modules.

    Attributes:
        params (NavigatorTaskParams): Parameters for configuring navigation modules.
        path_planner (BasePathPlanner): Instantiated path planner strategy.
        trajectory_planner (BaseTrajectoryPlanner): Instantiated trajectory planner strategy.
        avoidance (BaseAvoidance): Instantiated obstacle avoidance component.
    """

    def __init__(self, params: NavigatorTaskParams):
        """
        Initialize the NavigatorTask with the provided parameters.

        Args:
            params (NavigatorTaskParams): Configuration parameters for planners and avoidance.
        """
        self.params: NavigatorTaskParams = params

        # Instantiate the components
        self.path_planner: BasePathPlanner = PathPlannerFactory.instantiate(
            params.path_planner_params,
        )
        self.trajectory_planner: BaseTrajectoryPlanner = (
            TrajectoryPlannerFactory.instantiate(
                params.trajectory_planner_params,
                params.speed_profiler,
            )
        )
        self.avoidance: BaseAvoidance = AvoidanceFactory.instantiate(
            params.avoidance_params,
        )

        self.current_trajectory_plan_command: TrajectoryPlanCommand | None = None
        self.state: NavigatorTaskState = NavigatorTaskState.NOT_PLANNED

        self._start_time: float = 0.0

    def _create_path_planner_path_plan_params(
        self,
        current_position: OrientedPoint,
        goal: OrientedPoint,
    ) -> BasePathPlannerPlanPathParams:
        if (
            self.params.path_planner_params.path_finding_strategy
            == PathPlanningStrategy.DELTA
        ):
            return DeltaPathPlannerPlanPathParams(
                start=current_position,
            )
        if (
            self.params.path_planner_params.path_finding_strategy
            == PathPlanningStrategy.BASIC
        ):
            return BasicPathPlannerPlanPathParams(
                start=current_position,
                goal=goal,
            )

    def plan_task(self, params: BasePathPlannerPlanPathParams) -> None:
        self._start_time = time.time()
        path: list[OrientedPoint] = self.path_planner.plan_path(params)
        self.trajectory_planner.plan_trajectory(path)

    def _is_timeout(self) -> bool:
        """
        Check if the task has timed out.

        Returns:
            bool: True if the task has timed out, False otherwise.
        """
        return (
            self.params.timeout is not None  # Timeout is set
            and self._start_time != 0.0
            and time.time() - self._start_time > self.params.timeout
        )

    def _handle_timeout(self) -> None:
        """
        Handle the timeout condition by stopping the current task.
        """
        self.state = NavigatorTaskState.ABORT
        self.current_trajectory_plan_command = (
            TrajectoryPlanCommand.create_stop_command(
                current_position=self.params.goal,
            )
        )

    def _is_task_finished(self) -> bool:
        """
        Check if the task is finished.

        Returns:
            bool: True if the task is finished, False otherwise.
        """
        return (
            self._start_time != 0.0
            and self.state != NavigatorTaskState.FINISHED
            and time.time() - self._start_time
            > self.trajectory_planner.get_total_duration()
        )

    def handle(
        self, ally_zone: AllyZone, enemy_zone: EnemyZone
    ) -> TrajectoryPlanCommand:
        # Planned task before handle it if it is not already planned
        if self.state == NavigatorTaskState.NOT_PLANNED:
            self.plan_task(
                self._create_path_planner_path_plan_params(
                    current_position=ally_zone.point, goal=self.params.goal
                )
            )
            self.state = NavigatorTaskState.IN_PROGRESS

        # Check if task timeout is reached
        if self._is_timeout():
            self._handle_timeout()
            return self.current_trajectory_plan_command

        # Check if the task is finished
        if self._is_task_finished():
            self.state = NavigatorTaskState.FINISHED

        # Check avoidance
        self.avoidance.handle(
            current_navigator_task=self, ally_zone=ally_zone, enemy_zone=enemy_zone
        )

        # No need to check original trajectory plan because we are avoiding enemy
        if self.state == NavigatorTaskState.AVOIDING:
            return self.current_trajectory_plan_command

        # Check for classic trajectory execution
        self.current_trajectory_plan_command = self.trajectory_planner.get_plan()

        return self.current_trajectory_plan_command
