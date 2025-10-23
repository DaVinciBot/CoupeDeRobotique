"""Planner that splits a path into time-parameterized segments."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, override

from geometry import OrientedPoint
from navigation.trajectory_planner.base_trajectory_planner import BaseTrajectoryPlanner
from navigation.trajectory_planner.segments import (
    BaseSegment,
    RotationSegment,
    SegmentMapper,
    StopSegment,
    StraightSegment,
)
from navigation.trajectory_planner.sequential_trajectory_planner.sequential_trajectory_planner_params import (  # noqa: E501
    SequentialTrajectoryPlannerParams,
)
from navigation.trajectory_planner.structs import TrajectoryPlanCommand

if TYPE_CHECKING:
    from loggerplusplus import Logger

    from navigation.trajectory_planner.speed_profile import SpeedProfiler


class SequentialTrajectoryPlanner(
    BaseTrajectoryPlanner[SequentialTrajectoryPlannerParams],
):
    """Planner that constructs a sequential series of trajectory segments.

    This planner decomposes a given path of oriented waypoints into a sequence of
    trajectory segments (rotate, move straight, rotate, stop) from a path of oriented
    points.
    Supports time-based segment retrieval to provide motion commands.
    """

    def __init__(
        self,
        params: SequentialTrajectoryPlannerParams,
        speed_profiler: SpeedProfiler,
        logger: Logger | None = None,
    ) -> None:
        """Initialize the sequential trajectory planner with required parameters.

        Args:
            params (SequentialTrajectoryPlannerParams): Planning parameters.
            speed_profiler (SpeedProfiler): Speed profiler to control segment durations.
            logger (Logger | None, optional):
                Logger instance for debugging. Defaults to None.
        """
        super().__init__(params, speed_profiler, logger)
        self.segments_mapper: SegmentMapper | None = None
        self._last_call_time: float = 0.0

    @staticmethod
    def _normalize_angle(angle: float) -> float:
        angle = (angle + math.pi) % (2 * math.pi)
        if angle < 0:
            angle += 2 * math.pi
        return angle - math.pi

    def _compute_rotation_segment_to_be_front(
        self,
        start: OrientedPoint,
        target: OrientedPoint,
    ) -> RotationSegment:
        """Compute a rotation segment so the robot faces the next waypoint.

        Args:
            start (OrientedPoint): Current robot pose.
            target (OrientedPoint): Next waypoint pose (x, y, theta).

        Returns:
            RotationSegment: Segment rotating in place to face the waypoint.

        Raises:
            ValueError: If `start.theta` is None.
        """
        if start.theta is None:
            msg = "Start orientation (theta) must be defined."
            raise ValueError(msg)

        # Compute the absolute heading of the line from start to target
        path_theta = start.angle(target)
        # If reversing, we want the rear to face the target: add π to the heading
        desired_theta = path_theta + (math.pi if self._is_backward else 0)

        # Compute minimal rotation from current heading to ``desired_theta``
        delta_theta = self._normalize_angle(desired_theta - start.theta)

        # Build the intermediate oriented point after rotation
        intermediate_pose = OrientedPoint(start.x, start.y, desired_theta)

        # Create and return the rotation segment
        return RotationSegment(
            start_position=start,
            end_position=intermediate_pose,
            duration=self.speed_profiler.angular_speed_profile.get_total_duration(
                abs(delta_theta),
            ),
            rotation=abs(delta_theta),
            sign=1 if delta_theta > 0 else -1,
        )

    def _compute_rotation_segment_to_get_same_orientation(
        self,
        start: OrientedPoint,
        target: OrientedPoint,
    ) -> RotationSegment:
        """Compute a rotation segment so final orientation matches ``target``.

        Args:
            start (OrientedPoint): Robot pose after moving straight to the waypoint.
            target (OrientedPoint): Desired final waypoint pose (x, y, theta).

        Returns:
            RotationSegment: Segment rotating in place to align with target orientation.

        Raises:
            ValueError: If `start.theta` or `target.theta` is None.
        """
        if start.theta is None or target.theta is None:
            msg = "Start and target orientation (theta) must be defined."
            raise ValueError(msg)

        # Desired final heading: target.theta plus π if reversing
        desired_theta = target.theta + (math.pi if self._is_backward else 0)

        # Compute the minimal delta angle to rotate from current theta to desired_theta
        delta_theta = self._normalize_angle(desired_theta - start.theta)

        # Build the intermediate oriented point after rotation
        intermediate_pose = OrientedPoint(start.x, start.y, desired_theta)

        # Create and return the rotation segment
        return RotationSegment(
            start_position=start,
            end_position=intermediate_pose,
            duration=self.speed_profiler.angular_speed_profile.get_total_duration(
                abs(delta_theta),
            ),
            rotation=abs(delta_theta),
            sign=1 if delta_theta > 0 else -1,
        )

    def _compute_straight_segment(
        self,
        start: OrientedPoint,
        target: OrientedPoint,
    ) -> StraightSegment:
        """Compute straight segment needed to reach the next waypoint.

        Args:
            start (OrientedPoint): Start pose after initial rotation.
            target (OrientedPoint): Target waypoint.

        Returns:
            StraightSegment: Segment that moves in a straight line.
        """
        # Compute delta-distance
        delta_distance = start.distance(target)

        # Compute intermediate target position (start + distance)
        target = OrientedPoint(target.x, target.y, start.theta)

        return StraightSegment(
            start_position=start,
            end_position=target,
            duration=self.speed_profiler.linear_speed_profile.get_total_duration(
                delta_distance,
            ),
            distance=delta_distance,
        )

    @override
    def plan_trajectory(self, path: list[OrientedPoint]) -> None:
        """Build trajectory plan from a list of waypoints.

        Args:
            path (list[OrientedPoint]): List of oriented points representing the path.
        """
        # Initialize the segment list
        segments: list[BaseSegment] = []
        # Iterate over each pair of consecutive waypoints
        for i in range(len(path) - 1):
            start = path[i]
            target = path[i + 1]

            # 1. Compute rotation to face the next waypoint
            rotation_segment = self._compute_rotation_segment_to_be_front(
                start,
                target,
            )
            segments.append(rotation_segment)

            # 2. Compute straight-line segment to reach the waypoint
            straight_segment = self._compute_straight_segment(
                rotation_segment.end_position,
                target,
            )
            segments.append(straight_segment)

            # 3. Compute rotation to align with waypoint orientation
            # Apply to intermediates if ``respect_intermediate_orientation`` is set
            # or to the final goal if ``respect_goal_orientation`` is set
            if target.theta is not None and (
                self.params.respect_intermediate_orientation
                or (self.params.respect_goal_orientation and i == len(path) - 2)
            ):
                rotation_segment = (
                    self._compute_rotation_segment_to_get_same_orientation(
                        straight_segment.end_position,
                        target,
                    )
                )
                segments.append(rotation_segment)
            else:
                # Override orientation to current heading to skip rotation
                path[i + 1] = OrientedPoint(
                    path[i + 1].x,
                    path[i + 1].y,
                    straight_segment.end_position.theta,
                )

            # 4. Add a stop segment if a pause is configured
            if self.params.step_sleep_delay > 0:
                if target.theta is None:
                    target = OrientedPoint(
                        target.x,
                        target.y,
                        straight_segment.end_position.theta,
                    )
                segments.append(
                    StopSegment(
                        start_position=target,
                        end_position=target,
                        duration=self.params.step_sleep_delay,
                    ),
                )

        # Store the mapped segments for execution
        self.segments_mapper = SegmentMapper(segments)

    @BaseTrajectoryPlanner.ensure_planning_started
    def get_plan(self) -> TrajectoryPlanCommand:
        """Retrieve the current motion command based on elapsed time.

        Returns:
            TrajectoryPlanCommand: The motion command for the current time.

        Raises:
            RuntimeError: If the trajectory has not been planned yet.
            TypeError: If the segment type is unsupported.
        """
        # Get the current time elapsed
        time_elapsed = self._get_trajectory_time_elapsed()

        # Get the active segment
        if self.segments_mapper is None:
            msg = "Trajectory has not been planned yet."
            raise RuntimeError(msg)
        segment, local_time = self.segments_mapper.get_segment_at_time(time_elapsed)

        # If no segment is found -> plan is over -> stop the robot at the end path
        if segment is None:
            trajectory_plan_command = TrajectoryPlanCommand.create_stop_command(
                current_position=self.segments_mapper.get_last_segment().end_position,
            )

        # If the segment is a rotation segment
        elif isinstance(segment, RotationSegment):
            return self._get_rotation_command(segment, local_time)

        # If the segment is a straight segment
        elif isinstance(segment, StraightSegment):
            return self._get_straight_command(segment, local_time)

        # If the segment is a stop segment
        elif isinstance(segment, StopSegment):
            trajectory_plan_command = TrajectoryPlanCommand.create_stop_command(
                current_position=segment.start_position,
            )

        else:
            msg = f"Unsupported segment type: {type(segment)}.\n"
            msg += "Expected RotationSegment, StraightSegment, or StopSegment."
            raise TypeError(msg)

        # Save the last call time
        self._last_call_time: float = time_elapsed

        return trajectory_plan_command

    @override
    def get_total_duration(self) -> float:
        """Get the total planned duration of the trajectory.

        Returns:
            float: Total duration of the full trajectory.

        Raises:
            RuntimeError: If the trajectory has not been planned yet.
        """
        if self.segments_mapper is None:
            msg = "Trajectory has not been planned yet."
            raise RuntimeError(msg)
        return self.segments_mapper.cumulative_durations[-1]
