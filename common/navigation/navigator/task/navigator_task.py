# ====== Code Summary ======
# This module defines the NavigatorTask class, which orchestrates path planning, trajectory planning,
# and obstacle avoidance for autonomous navigation. Based on provided configuration parameters,
# it dynamically instantiates components like planners (Delta, Basic, Sequential) and the stop-and-wait
# avoidance strategy. It manages the navigation lifecycle through methods for planning, timeout handling,
# completion detection, and reactive avoidance execution.

import time
from typing import TYPE_CHECKING

from arena import AllyZone, EnemyZone
from navigation.navigator.task.navigator_task_params import NavigatorTaskParams
from navigation.navigator.task.states import NavigatorTaskState
from navigation.path_planner import (
    BasePathPlanner,
    BasePathPlannerPlanPathParams,
    PathPlannerFactory,
    PathPlannerPathPlanParamsFactory,
)
from navigation.trajectory_planner import (
    BaseTrajectoryPlanner,
    TrajectoryPlanCommand,
    TrajectoryPlannerFactory,
)

if TYPE_CHECKING:
    from geometry import OrientedPoint


class NavigatorTask:
    """A task responsible for executing autonomous navigation including path planning,
    trajectory generation, obstacle avoidance, and a stabilization timer after reaching the goal.
    """

    def __init__(self, params: NavigatorTaskParams) -> None:
        """Initialize the NavigatorTask.

        Args:
            params (NavigatorTaskParams): The parameters for the navigation task.
        """
        from navigation.avoidance import AvoidanceFactory, BaseAvoidance

        self.params = params
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
            params.acs_detection_profile_params,
        )
        self.current_trajectory_command: TrajectoryPlanCommand | None = None
        self.state: NavigatorTaskState = NavigatorTaskState.NOT_PLANNED
        self._start_time: float | None = None
        self._stabilization_start_time: float | None = None

    def _get_elapsed_time(self) -> float:
        if self._start_time is None:
            return 0.0
        return time.time() - self._start_time

    def _get_stabilization_elapsed(self) -> float:
        if self._stabilization_start_time is None:
            return 0.0
        return time.time() - self._stabilization_start_time

    def _plan_task(self, ally_zone: AllyZone) -> None:
        self._start_time = time.time()
        plan_path_params: BasePathPlannerPlanPathParams = (
            PathPlannerPathPlanParamsFactory.instantiate(
                strategy=self.params.path_planner_params.path_finding_strategy,
                current_position=ally_zone.point,
                goal=self.params.goal,
            )
        )
        path: list[OrientedPoint] = self.path_planner.plan_path(plan_path_params)
        self.trajectory_planner.plan_trajectory(path)
        self.current_trajectory_command = self.trajectory_planner.get_plan()
        self.state = NavigatorTaskState.IN_PROGRESS

    def _has_timed_out(self) -> bool:
        return (
            False
            if self.params.timeout is None or self._start_time is None
            else (self._get_elapsed_time() > self.params.timeout)
        )

    def _abort(self) -> TrajectoryPlanCommand:
        self.state = NavigatorTaskState.ABORT
        self.current_trajectory_command = TrajectoryPlanCommand.create_stop_command(
            current_position=self.params.goal,
        )
        return self.current_trajectory_command

    def _is_finished(self) -> bool:
        if self._start_time is None or self.state == NavigatorTaskState.FINISHED:
            return False
        return self._get_elapsed_time() > self.trajectory_planner.get_total_duration()

    def handle(
        self,
        ally_zone: AllyZone,
        enemy_zone: EnemyZone,
    ) -> TrajectoryPlanCommand:
        # 1. Initial planning
        if self.state == NavigatorTaskState.NOT_PLANNED:
            self._plan_task(ally_zone)
            return self.trajectory_planner.get_plan()

        # 2. Timeout check
        if self._has_timed_out():
            return self._abort()

        # 3. Completion detection
        if self._is_finished() and self.state != NavigatorTaskState.STABILIZING:
            # Start stabilization timer
            if self.params.stabilization_delay > 0:
                self._stabilization_start_time = time.time()
                self.state = NavigatorTaskState.STABILIZING
                # keep last trajectory command
                return self.trajectory_planner.get_plan()

            # No stabilization: finish immediately with stop
            self.state = NavigatorTaskState.FINISHED
            return self.trajectory_planner.get_plan()

        # 4. Stabilization period: replay last trajectory command
        if self.state == NavigatorTaskState.STABILIZING:
            if self._get_stabilization_elapsed() < self.params.stabilization_delay:
                return self.trajectory_planner.get_plan()
            # Timer expired: finish and send stop
            self.state = NavigatorTaskState.FINISHED
            return self.trajectory_planner.get_plan()

        # 5. Obstacle avoidance
        avoidance_cmd = self.avoidance.handle(
            current_navigator_task=self,
            ally_zone=ally_zone,
            enemy_zone=enemy_zone,
        )
        if self.state == NavigatorTaskState.AVOIDING:
            return avoidance_cmd

        # 6. Continue normal trajectory
        self.current_trajectory_command = self.trajectory_planner.get_plan()
        return self.current_trajectory_command
