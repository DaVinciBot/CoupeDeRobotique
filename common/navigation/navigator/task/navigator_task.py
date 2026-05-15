"""Navigator task handling planning, avoidance, and stabilization."""

from __future__ import annotations

import math
import time
from typing import TYPE_CHECKING, cast

from navigation.navigator.task.states import NavigatorTaskState
from navigation.path_planner import (
    PathPlannerFactory,
    PathPlannerPathPlanParamsFactory,
    PathPlanningStrategy,
)
from navigation.trajectory_planner import (
    TrajectoryPlanCommand,
    TrajectoryPlannerFactory,
)

TRACKING_LOOKAHEAD_S = 0.25
SPEED_EPSILON = 1e-9

if TYPE_CHECKING:
    from arena.base_arena.arena_zones import AllyZone, EnemyZone
    from geometry import OrientedPoint
    from navigation.avoidance.base_avoidance import BaseAvoidance, BaseAvoidanceParams
    from navigation.navigator.task.navigator_task_params import NavigatorTaskParams
    from navigation.path_planner.base_path_planner import (
        BasePathPlanner,
        BasePathPlannerParams,
        BasePathPlannerPlanPathParams,
    )
    from navigation.trajectory_planner.base_trajectory_planner import (
        BaseTrajectoryPlanner,
        BaseTrajectoryPlannerParams,
    )


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
        self.path_planner: BasePathPlanner[
            BasePathPlannerParams,
            BasePathPlannerPlanPathParams,
        ] = PathPlannerFactory.instantiate(
            params.path_planner_params,
        )
        self.trajectory_planner: BaseTrajectoryPlanner[BaseTrajectoryPlannerParams] = (
            TrajectoryPlannerFactory.instantiate(
                params.trajectory_planner_params,
                params.speed_profiler,
            )
        )
        self.avoidance: BaseAvoidance[BaseAvoidanceParams] = (
            AvoidanceFactory.instantiate(
                params.avoidance_params,
                params.acs_detection_profile_params,
            )
        )
        self.current_trajectory_command: TrajectoryPlanCommand | None = None
        self.state: NavigatorTaskState = NavigatorTaskState.NOT_PLANNED
        self._start_time: float | None = None
        self._stabilization_start_time: float | None = None
        self._planned_goal: OrientedPoint | None = None

    @staticmethod
    def _normalize_angle(angle: float) -> float:
        angle = (angle + math.pi) % (2 * math.pi)
        if angle < 0:
            angle += 2 * math.pi
        return angle - math.pi

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
        self._planned_goal = path[-1] if path else ally_zone.point
        self.trajectory_planner.plan_trajectory(path)
        self.current_trajectory_command = self.trajectory_planner.get_plan()
        self.state = NavigatorTaskState.IN_PROGRESS

    def _has_timed_out(self) -> bool:
        return (
            False
            if self.params.timeout is None or self._start_time is None
            else self._get_elapsed_time() > self.params.timeout
        )

    def _abort(self, current_position: OrientedPoint) -> TrajectoryPlanCommand:
        self.state = NavigatorTaskState.ABORT
        self.current_trajectory_command = TrajectoryPlanCommand.create_stop_command(
            current_position=current_position,
        )
        return self.current_trajectory_command

    def start_replanned_trajectory(
        self,
        path: list[OrientedPoint],
        current_position: OrientedPoint,
    ) -> TrajectoryPlanCommand:
        self._planned_goal = path[-1] if path else current_position
        self.trajectory_planner.plan_trajectory(path)
        self.trajectory_planner.start_planning()
        self._start_time = time.time()
        self._stabilization_start_time = None
        self.state = NavigatorTaskState.IN_PROGRESS

        planned_cmd = self.trajectory_planner.get_plan()
        self.current_trajectory_command = self._command_from_current_position(
            planned_cmd,
            current_position,
        )
        return self.current_trajectory_command

    def start_replanned_trajectory_from_current_position(
        self,
        current_position: OrientedPoint,
    ) -> TrajectoryPlanCommand:
        """Replan after avoidance without restarting relative delta tasks.

        Delta tasks already computed an absolute ``_planned_goal`` during the
        initial plan. Reusing their original delta from the current position would
        repeat the full relative move after every avoidance interruption.
        """
        if (
            self.params.path_planner_params.path_finding_strategy
            == PathPlanningStrategy.DELTA
            and self._planned_goal is not None
        ):
            return self.start_replanned_trajectory(
                [current_position, self._planned_goal],
                current_position,
            )

        last_params = cast(
            "BasePathPlannerPlanPathParams",
            self.path_planner.last_plan_path_params,
        )
        last_params.start = current_position
        return self.start_replanned_trajectory(
            self.path_planner.plan_path(last_params),
            current_position,
        )

    def _is_goal_reached(self, current_position: OrientedPoint) -> bool:
        goal = self._planned_goal or self.params.goal
        if goal is None:
            return False

        if current_position.distance(goal) > self.params.position_reached_tolerance_cm:
            return False

        if current_position.theta is None or goal.theta is None:
            return True

        return (
            abs(self._normalize_angle(goal.theta - current_position.theta))
            <= self.params.angle_reached_tolerance_rad
        )

    def _is_finished(self, current_position: OrientedPoint) -> bool:
        if self._start_time is None or self.state == NavigatorTaskState.FINISHED:
            return False
        total_duration = self.trajectory_planner.get_total_duration()
        elapsed_time = self._get_elapsed_time()
        if elapsed_time <= total_duration:
            return False
        if self._is_goal_reached(current_position):
            return True
        finish_delay = self.params.finish_after_expected_end_delay_s
        return (
            finish_delay is not None
            and elapsed_time > total_duration + finish_delay
        )

    def _command_from_current_position(
        self,
        planned_cmd: TrajectoryPlanCommand,
        current_position: OrientedPoint,
    ) -> TrajectoryPlanCommand:
        """Rebase the trajectory command on the measured robot pose.

        The trajectory planner produces a time-indexed theoretical pose. The motor
        controller, however, should chase a local target built from the real
        odometry so a lagging robot does not keep receiving targets that run away
        along the ideal trajectory.

        Returns:
            TrajectoryPlanCommand: Command rebased on the measured pose.
        """
        from geometry import OrientedPoint  # noqa: PLC0415

        goal = self._planned_goal or planned_cmd.position
        trajectory_is_over = (
            self._get_elapsed_time() >= self.trajectory_planner.get_total_duration()
        )
        if trajectory_is_over:
            return TrajectoryPlanCommand(
                position=goal,
                linear_speed=0.0,
                angular_speed=0.0,
            )

        if current_position.theta is None:
            return planned_cmd

        target_theta = current_position.theta
        has_angular_speed = abs(planned_cmd.angular_speed) > SPEED_EPSILON
        has_linear_speed = abs(planned_cmd.linear_speed) > SPEED_EPSILON

        if has_angular_speed:
            target_theta = current_position.theta + (
                planned_cmd.angular_speed * TRACKING_LOOKAHEAD_S
            )
        elif planned_cmd.position.theta is not None:
            target_theta = planned_cmd.position.theta

        dx = 0.0
        dy = 0.0
        if has_linear_speed:
            heading = (
                planned_cmd.position.theta
                if planned_cmd.position.theta is not None
                else current_position.theta
            )
            step = planned_cmd.linear_speed * TRACKING_LOOKAHEAD_S
            max_step = current_position.distance(goal)
            if abs(step) > max_step:
                step = math.copysign(max_step, step)
            dx = step * math.cos(heading)
            dy = step * math.sin(heading)

        if not has_linear_speed and not has_angular_speed:
            target = current_position
        else:
            target = OrientedPoint(
                (current_position.x + dx, current_position.y + dy),
                target_theta,
            )

        return TrajectoryPlanCommand(
            position=target,
            linear_speed=planned_cmd.linear_speed,
            angular_speed=planned_cmd.angular_speed,
        )

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
            planned_cmd = self.trajectory_planner.get_plan()
            self.current_trajectory_command = self._command_from_current_position(
                planned_cmd,
                ally_zone.point,
            )
            return self.current_trajectory_command

        if self._has_timed_out():
            return self._abort(ally_zone.point)

        if self.state == NavigatorTaskState.AVOIDING:
            return self.avoidance.handle(
                current_navigator_task=self,
                ally_zone=ally_zone,
                enemy_zone=enemy_zone,
            )

        planned_cmd = self.trajectory_planner.get_plan()
        cmd = self._command_from_current_position(planned_cmd, ally_zone.point)

        if (
            self._is_finished(ally_zone.point)
            and self.state != NavigatorTaskState.STABILIZING
        ):
            if self.params.stabilization_delay > 0:
                self._stabilization_start_time = time.time()
                self.state = NavigatorTaskState.STABILIZING
            else:
                self.state = NavigatorTaskState.FINISHED

        if self.state == NavigatorTaskState.STABILIZING:
            if self._get_stabilization_elapsed() < self.params.stabilization_delay:
                self.current_trajectory_command = (
                    TrajectoryPlanCommand.create_stop_command(
                        current_position=ally_zone.point,
                    )
                )
                return self.current_trajectory_command
            self.state = NavigatorTaskState.FINISHED

        if self.state == NavigatorTaskState.FINISHED:
            self.current_trajectory_command = TrajectoryPlanCommand.create_stop_command(
                current_position=ally_zone.point,
            )
            return self.current_trajectory_command

        self.current_trajectory_command = cmd

        avoidance_cmd = self.avoidance.handle(
            current_navigator_task=self,
            ally_zone=ally_zone,
            enemy_zone=enemy_zone,
        )
        if self.state == NavigatorTaskState.AVOIDING:
            return avoidance_cmd

        return self.current_trajectory_command
