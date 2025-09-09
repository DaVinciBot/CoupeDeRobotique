"""Navigator task handling planning, avoidance, and stabilization."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, cast

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
    from arena import AllyZone, EnemyZone
    from geometry import OrientedPoint
    from navigation.avoidance.base_avoidance import BaseAvoidance
    from navigation.navigator.task.navigator_task_params import NavigatorTaskParams


class NavigatorTask:
    """Execute autonomous navigation, including path planning and avoidance."""

    def __init__(self, params: NavigatorTaskParams) -> None:
        """Initialize the NavigatorTask.

        Args:
            params (NavigatorTaskParams): The parameters for the navigation task.

        """
        from navigation.avoidance.avoidance_factory import (  # noqa: PLC0415
            AvoidanceFactory,
        )

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
                goal=cast("OrientedPoint", self.params.goal),
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
            else self._get_elapsed_time() > self.params.timeout
        )

    def _abort(self) -> TrajectoryPlanCommand:
        self.state = NavigatorTaskState.ABORT
        self.current_trajectory_command = TrajectoryPlanCommand.create_stop_command(
            current_position=cast("OrientedPoint", self.params.goal),
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
        """Advance the task and return the next trajectory command.

        Args:
            ally_zone (AllyZone): The ally zone information.
            enemy_zone (EnemyZone): The enemy zone information.

        Returns:
            TrajectoryPlanCommand: Next trajectory command.

        """
        if self.state == NavigatorTaskState.NOT_PLANNED:
            self._plan_task(ally_zone)
            return self.trajectory_planner.get_plan()

        if self._has_timed_out():
            return self._abort()

        cmd = self.trajectory_planner.get_plan()

        if self._is_finished() and self.state != NavigatorTaskState.STABILIZING:
            if self.params.stabilization_delay > 0:
                self._stabilization_start_time = time.time()
                self.state = NavigatorTaskState.STABILIZING
            else:
                self.state = NavigatorTaskState.FINISHED

        if self.state == NavigatorTaskState.STABILIZING:
            if self._get_stabilization_elapsed() < self.params.stabilization_delay:
                return cmd
            self.state = NavigatorTaskState.FINISHED

        if self.state == NavigatorTaskState.FINISHED:
            return cmd

        avoidance_cmd = self.avoidance.handle(
            current_navigator_task=self,
            ally_zone=ally_zone,
            enemy_zone=enemy_zone,
        )
        if self.state == NavigatorTaskState.AVOIDING:
            return avoidance_cmd

        self.current_trajectory_command = cmd
        return self.current_trajectory_command
