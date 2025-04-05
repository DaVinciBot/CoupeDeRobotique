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
    DeltaPathPlanner, DeltaPathPlannerParams, DeltaPathPlannerPlanPathParams,
    BasicPathPlanner, BasicPathPlannerParams, BasicPathPlannerPlanPathParams
)
from navigation.trajectory_planner import (
    # Strategy
    TrajectoryPlannerStrategy,

    # Base class
    BaseTrajectoryPlanner,

    # Derivative classes
    SequentialTrajectoryPlanner, SequentialTrajectoryPlannerParams,
)
from navigation.avoidance import BaseAvoidance, AvoidanceStrategy, StopAndWaitAvoidance, StopAndWaitAvoidanceParams

from navigation.navigator.task import NavigatorTaskParams

from arena import AllyZone, EnemyZone
from navigation.trajectory_planner import TrajectoryPlanCommand
from navigation.navigator.task.states import NavigatorTaskState

from navigation.path_planner import BasePathPlannerPlanPathParams
from geometry import OrientedPoint


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
        self.path_planner: BasePathPlanner = self._instantiate_path_planner()
        self.trajectory_planner: BaseTrajectoryPlanner = self._instantiate_trajectory_planner()
        self.avoidance: BaseAvoidance = self._instantiate_avoidance()

        self.current_trajectory_plan_command: TrajectoryPlanCommand | None = None
        self.state: NavigatorTaskState = NavigatorTaskState.NOT_PLANNED

        self._start_time: float = 0.0

    def _instantiate_path_planner(self) -> BasePathPlanner:
        """
        Instantiate the path planner based on the configured strategy.

        Returns:
            BasePathPlanner: The appropriate path planner instance.
        """
        # Delta strategy
        if self.params.path_planner_params.path_finding_strategy == PathPlanningStrategy.DELTA:
            return DeltaPathPlanner(
                cast(DeltaPathPlannerParams, self.params.path_planner_params)
            )

        # Basic strategy
        if self.params.path_planner_params.path_finding_strategy == PathPlanningStrategy.BASIC:
            return BasicPathPlanner(
                cast(BasicPathPlannerParams, self.params.path_planner_params)
            )

        # ASTAR strategy
        # TODO: to implement
        # if self.params.path_planner.path_finding_strategy == PathPlanningStrategy.ASTAR:
        #     return AStarPathPlanner(
        #         cast(AStarPathPlannerParams, self.params.path_planner)
        #     )

        raise ValueError("Unsupported path planning strategy provided.")

    def _instantiate_trajectory_planner(self) -> BaseTrajectoryPlanner:
        """
        Instantiate the trajectory planner based on the configured strategy.

        Returns:
            BaseTrajectoryPlanner: The appropriate trajectory planner instance.
        """
        # Sequential strategy
        if self.params.trajectory_planner_params.trajectory_planning_strategy == TrajectoryPlannerStrategy.SEQUENTIAL:
            return SequentialTrajectoryPlanner(
                cast(SequentialTrajectoryPlannerParams, self.params.trajectory_planner_params),
                self.params.speed_profiler
            )

        raise ValueError("Unsupported trajectory planning strategy provided.")

    def _instantiate_avoidance(self) -> BaseAvoidance:
        """
        Instantiate the obstacle avoidance component.

        Returns:
            BaseAvoidance: The avoidance instance.
        """
        # Stop and wait strategy
        if self.params.avoidance_params.avoidance_strategy == AvoidanceStrategy.STOP_AND_WAIT:
            return StopAndWaitAvoidance(
                cast(StopAndWaitAvoidanceParams, self.params.avoidance_params)
            )

    def _create_path_planner_path_plan_params(
            self,
            current_position: OrientedPoint,
            goal: OrientedPoint,
    ) -> BasePathPlannerPlanPathParams:
        if self.params.path_planner_params.path_finding_strategy == PathPlanningStrategy.DELTA:
            return DeltaPathPlannerPlanPathParams(
                start=current_position,
            )
        if self.params.path_planner_params.path_finding_strategy == PathPlanningStrategy.BASIC:
            return BasicPathPlannerPlanPathParams(
                start=current_position,
                goal=goal,
            )

    def plan_task(self, params: BasePathPlannerPlanPathParams) -> None:
        self._start_time = time.time()
        path: list[OrientedPoint] = self.path_planner.plan_path(params)
        self.trajectory_planner.plan_trajectory(path)

    def handle(self, ally_zone: AllyZone, enemy_zone: EnemyZone) -> TrajectoryPlanCommand:
        # Planned task before handle it if it is not already planned
        if self.state == NavigatorTaskState.NOT_PLANNED:
            self.plan_task(
                self._create_path_planner_path_plan_params(
                    current_position=ally_zone.point,
                    goal=self.params.goal
                )
            )
            self.state = NavigatorTaskState.IN_PROGRESS

        # Check if task timeout is reached
        if (
                self.params.timeout is not None and  # Timeout is set
                self._start_time != 0.0 and
                time.time() - self._start_time > self.params.timeout
        ):
            self.state = NavigatorTaskState.ABORT
            self.current_trajectory_plan_command = TrajectoryPlanCommand.create_stop_command(
                current_position=ally_zone.point,
            )
            return self.current_trajectory_plan_command

        # Check if the task is finished
        if (
                self._start_time != 0.0 and
                self.state != NavigatorTaskState.FINISHED and
                time.time() - self._start_time > self.trajectory_planner.get_total_duration()
        ):
            self.state = NavigatorTaskState.FINISHED

        # Check avoidance
        self.avoidance.handle(
            current_navigator_task=self,
            ally_zone=ally_zone,
            enemy_zone=enemy_zone
        )
        # No need to check original trajectory plan because we are avoiding enemy
        if self.state == NavigatorTaskState.AVOIDING:
            return self.current_trajectory_plan_command

        # Check for classic trajectory execution
        self.current_trajectory_plan_command = self.trajectory_planner.get_plan()

        return self.current_trajectory_plan_command
