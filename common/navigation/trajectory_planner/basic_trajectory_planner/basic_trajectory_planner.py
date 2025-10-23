"""Planner that creates smooth curved trajectories from waypoints."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, override

from geometry import OrientedPoint
from navigation.trajectory_planner.base_trajectory_planner import BaseTrajectoryPlanner
from navigation.trajectory_planner.basic_trajectory_planner.basic_trajectory_planner_params import (  # noqa: E501
    BasicTrajectoryPlannerParams,
)
from navigation.trajectory_planner.segments import (
    BaseSegment,
    RotationSegment,
    SegmentMapper,
    SmoothSegment,
    StraightSegment,
)
from navigation.trajectory_planner.structs import TrajectoryPlanCommand

if TYPE_CHECKING:
    from loggerplusplus import Logger

    from navigation.trajectory_planner.speed_profile import SpeedProfiler

_MIN_POINTS_FOR_CURVE = 2
"""Minimum number of points needed ahead to create a curve."""
_MIN_PATH_LENGTH = 2
"""Minimum number of points required in a path."""
_FINAL_ORIENTATION_THRESHOLD = 0.01
"""Threshold (in radians) for determining if final rotation is needed."""


class BasicTrajectoryPlanner(BaseTrajectoryPlanner[BasicTrajectoryPlannerParams]):
    """Planner that creates trajectories with smooth curves.

    This planner analyzes a path and creates curved segments where consecutive
    waypoints can be smoothly connected, reducing the need for stop-and-turn
    maneuvers.
    """

    def __init__(
        self,
        params: BasicTrajectoryPlannerParams,
        speed_profiler: SpeedProfiler,
        logger: Logger | None = None,
    ) -> None:
        """Initialize the basic trajectory planner with required parameters.

        Args:
            params (BasicTrajectoryPlannerParams): Planning parameters.
            speed_profiler (SpeedProfiler): Speed profiler to control segment durations.
            logger (Logger | None, optional):
                Logger instance for debugging. Defaults to None.
        """
        super().__init__(params, speed_profiler, logger)
        self.segments_mapper: SegmentMapper | None = None

    def _can_create_curve(
        self,
        p1: OrientedPoint,
        p2: OrientedPoint,
        p3: OrientedPoint,
    ) -> bool:
        """Check if three consecutive points can form a smooth curve.

        Args:
            p1 (OrientedPoint): First waypoint.
            p2 (OrientedPoint): Middle waypoint.
            p3 (OrientedPoint): Third waypoint.

        Returns:
            bool: True if a curve can be created between these points.
        """
        angle1 = p1.angle(p2)
        angle2 = p2.angle(p3)

        angle_diff = abs(self._normalize_angle(angle2 - angle1))

        return angle_diff < self.params.curve_detection_angle_threshold

    def _compute_curve_segment(
        self,
        start: OrientedPoint,
        middle: OrientedPoint,
        end: OrientedPoint,
    ) -> SmoothSegment:
        """Create a smooth curved segment through three points.

        Args:
            start (OrientedPoint): Starting point.
            middle (OrientedPoint): Middle waypoint for curve.
            end (OrientedPoint): End point.

        Returns:
            SmoothSegment: Curved trajectory segment.
        """
        # Sample points along the curve using simple interpolation
        # TODO: use Bezier curves or splines for better smoothness
        num_samples = 10
        sampled_points: list[OrientedPoint] = []
        total_distance = 0.0

        for i in range(num_samples + 1):
            t = i / num_samples
            x = (1 - t) ** 2 * start.x + 2 * (1 - t) * t * middle.x + t**2 * end.x
            y = (1 - t) ** 2 * start.y + 2 * (1 - t) * t * middle.y + t**2 * end.y

            if i < num_samples:
                t_next = (i + 1) / num_samples
                x_next = (
                    (1 - t_next) ** 2 * start.x
                    + 2 * (1 - t_next) * t_next * middle.x
                    + t_next**2 * end.x
                )
                y_next = (
                    (1 - t_next) ** 2 * start.y
                    + 2 * (1 - t_next) * t_next * middle.y
                    + t_next**2 * end.y
                )
                theta = math.atan2(y_next - y, x_next - x)
            else:
                theta = sampled_points[-1].theta if sampled_points else 0.0

            point = OrientedPoint(x, y, theta)
            sampled_points.append(point)

            if i > 0:
                total_distance += sampled_points[i - 1].distance(point)

        if self._is_backward:
            for point in sampled_points:
                if point.theta is not None:
                    point.theta = self._normalize_angle(point.theta + math.pi)

        duration = self.speed_profiler.linear_speed_profile.get_total_duration(
            total_distance,
        )

        return SmoothSegment(
            start_position=sampled_points[0],
            end_position=sampled_points[-1],
            duration=duration,
            sampled_points=sampled_points,
            total_distance=total_distance,
        )

    def _compute_straight_segment(
        self,
        start: OrientedPoint,
        end: OrientedPoint,
    ) -> StraightSegment:
        """Create a straight segment between two points.

        Args:
            start (OrientedPoint): Starting point.
            end (OrientedPoint): Ending point.

        Returns:
            StraightSegment: Straight trajectory segment.
        """
        distance = start.distance(end)

        theta = start.angle(end)
        if self._is_backward:
            theta += math.pi

        start_oriented = OrientedPoint(start.x, start.y, theta)
        end_oriented = OrientedPoint(end.x, end.y, theta)

        return StraightSegment(
            start_position=start_oriented,
            end_position=end_oriented,
            duration=self.speed_profiler.linear_speed_profile.get_total_duration(
                distance,
            ),
            distance=distance,
        )

    def _compute_rotation_segment(
        self,
        start: OrientedPoint,
        target_theta: float,
    ) -> RotationSegment:
        """Create a rotation segment to reach target orientation.

        Args:
            start (OrientedPoint): Starting pose.
            target_theta (float): Target orientation in radians.

        Returns:
            RotationSegment: Rotation segment.

        Raises:
            ValueError: If start.theta is None.
        """
        if start.theta is None:
            msg = "Start orientation (theta) must be defined."
            raise ValueError(msg)

        delta_theta = self._normalize_angle(target_theta - start.theta)

        end_position = OrientedPoint(start.x, start.y, target_theta)

        return RotationSegment(
            start_position=start,
            end_position=end_position,
            duration=self.speed_profiler.angular_speed_profile.get_total_duration(
                abs(delta_theta),
            ),
            rotation=abs(delta_theta),
            sign=1 if delta_theta > 0 else -1,
        )

    @override
    def plan_trajectory(self, path: list[OrientedPoint]) -> None:
        """Build trajectory plan with smooth curves from waypoints.

        Args:
            path (list[OrientedPoint]): List of oriented points representing the path.
        """
        if len(path) < _MIN_PATH_LENGTH:
            self.logger.warning("Path must contain at least 2 points.")
            return

        segments: list[BaseSegment] = []

        i = 0
        min_path_length_for_curve = _MIN_POINTS_FOR_CURVE + 1
        while i < len(path) - 1:
            if i < len(path) - min_path_length_for_curve + 1 and self._can_create_curve(
                path[i],
                path[i + 1],
                path[i + 2],
            ):
                curve_segment = self._compute_curve_segment(
                    path[i],
                    path[i + 1],
                    path[i + 2],
                )
                segments.append(curve_segment)
                i += _MIN_POINTS_FOR_CURVE
            else:
                straight_segment = self._compute_straight_segment(path[i], path[i + 1])
                segments.append(straight_segment)
                i += 1

        if (
            self.params.respect_goal_orientation
            and path[-1].theta is not None
            and segments
        ):
            last_segment = segments[-1]
            final_theta = path[-1].theta
            if self._is_backward:
                final_theta = self._normalize_angle(final_theta + math.pi)

            if (
                last_segment.end_position.theta is not None
                and abs(
                    self._normalize_angle(
                        final_theta - last_segment.end_position.theta,
                    ),
                )
                > _FINAL_ORIENTATION_THRESHOLD
            ):
                rotation_segment = self._compute_rotation_segment(
                    last_segment.end_position,
                    final_theta,
                )
                segments.append(rotation_segment)

        self.segments_mapper = SegmentMapper(segments)
        self.logger.info(f"Planned trajectory with {len(segments)} segments.")

    def _get_smooth_command(
        self,
        segment: SmoothSegment,
        local_time: float | None,
    ) -> TrajectoryPlanCommand:
        """Get trajectory command for a smooth/curved segment.

        Args:
            segment (SmoothSegment): The smooth segment.
            local_time (float | None): Time elapsed within this segment.

        Returns:
            TrajectoryPlanCommand: Command for curved motion.
        """
        traveled_distance = self.speed_profiler.linear_speed_profile.get_distance(
            time_elapsed=local_time,
            distance=segment.total_distance,
        )

        accumulated_distance = 0.0
        target_point = segment.sampled_points[0]

        for i in range(1, len(segment.sampled_points)):
            prev_point = segment.sampled_points[i - 1]
            curr_point = segment.sampled_points[i]
            segment_distance = prev_point.distance(curr_point)

            if accumulated_distance + segment_distance >= traveled_distance:
                ratio = (
                    (traveled_distance - accumulated_distance) / segment_distance
                    if segment_distance > 0
                    else 0
                )
                x = prev_point.x + (curr_point.x - prev_point.x) * ratio
                y = prev_point.y + (curr_point.y - prev_point.y) * ratio

                theta = curr_point.theta

                target_point = OrientedPoint(x, y, theta)
                break

            accumulated_distance += segment_distance
        else:
            target_point = segment.sampled_points[-1]

        angular_speed = 0.0
        if len(segment.sampled_points) > 1:
            idx = min(
                int(
                    (traveled_distance / segment.total_distance)
                    * len(segment.sampled_points),
                ),
                len(segment.sampled_points) - 2,
            )
            idx_point = segment.sampled_points[idx]
            next_idx_point = segment.sampled_points[idx + 1]
            if idx_point.theta is not None and next_idx_point.theta is not None:
                angle_diff = self._normalize_angle(
                    next_idx_point.theta - idx_point.theta,
                )
                time_diff = segment.duration / len(segment.sampled_points)
                if time_diff > 0:
                    angular_speed = angle_diff / time_diff

        return TrajectoryPlanCommand(
            position=target_point,
            linear_speed=self.speed_profiler.linear_speed_profile.get_speed(
                time_elapsed=local_time,
                distance=segment.total_distance,
            ),
            angular_speed=angular_speed,
        )

    @BaseTrajectoryPlanner.ensure_planning_started
    def get_plan(self) -> TrajectoryPlanCommand:
        """Retrieve the current motion command based on elapsed time.

        Returns:
            TrajectoryPlanCommand: The motion command for the current time.

        Raises:
            RuntimeError: If the trajectory has not been planned yet.
            TypeError: If the segment type is unsupported.
        """
        if self.segments_mapper is None:
            msg = "Trajectory has not been planned yet."
            raise RuntimeError(msg)

        time_elapsed = self._get_trajectory_time_elapsed()

        segment, local_time = self.segments_mapper.get_segment_at_time(time_elapsed)

        if segment is None:
            return TrajectoryPlanCommand.create_stop_command(
                current_position=self.segments_mapper.get_last_segment().end_position,
            )

        if isinstance(segment, RotationSegment):
            return self._get_rotation_command(segment, local_time)

        if isinstance(segment, StraightSegment):
            return self._get_straight_command(segment, local_time)

        if isinstance(segment, SmoothSegment):
            return self._get_smooth_command(segment, local_time)

        msg = f"Unsupported segment type: {type(segment)}."
        msg += "Expected RotationSegment, StraightSegment or SmoothSegment."
        raise TypeError(msg)

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

    @staticmethod
    def _normalize_angle(angle: float) -> float:
        """Normalize angle to [-pi, pi] range.

        Args:
            angle (float): Angle in radians.

        Returns:
            float: Normalized angle.
        """
        angle = (angle + math.pi) % (2 * math.pi)
        if angle < 0:
            angle += 2 * math.pi
        return angle - math.pi
