import math
from math import sqrt, sin, cos, atan2
from dataclasses import dataclass
from loggerplusplus import Logger
from geometry import OrientedPoint
from navigation.trajectory_planner.structs import TrajectoryPlanCommand
from navigation.trajectory_planner.base_trajectory_planner.base_trajectory_planner import BaseTrajectoryPlanner
from navigation.trajectory_planner.dummy_trajectory_planner.dummy_trajectory_planner_params import \
    DummyTrajectoryPlannerParams

from navigation.trajectory_planner.speed_profile import SpeedProfiler
from navigation.trajectory_planner.dummy_trajectory_planner.segments import (
    BaseSegment, StraightSegment, RotationSegment, StopSegment, SegmentMapper
)


class DummyTrajectoryPlanner(BaseTrajectoryPlanner[DummyTrajectoryPlannerParams]):
    def __init__(
            self,
            params: DummyTrajectoryPlannerParams,
            speed_profiler: SpeedProfiler,
            logger: Logger | None = None
    ) -> None:
        super().__init__(params, speed_profiler, logger)

        self.segments_mapper: SegmentMapper | None = None

        self._last_call_time: float = 0.0

    def _compute_rotation_segment(self, start: OrientedPoint, target: OrientedPoint) -> RotationSegment:
        # Compute delta-theta to rotate in front of the target
        d_theta = math.atan2(target.y - start.y, target.x - start.x) - start.theta

        return RotationSegment(
            start_position=start,
            end_position=target,
            duration=self.speed_profiler.angular_speed_profile.get_total_duration(d_theta),
            rotation=d_theta
        )

    def _compute_straight_segment(self, start: OrientedPoint, target: OrientedPoint) -> StraightSegment:
        # Compute delta-distance
        delta_distance = start.distance(target)  # Use shapely method for more performance

        return StraightSegment(
            start_position=start,
            end_position=target,
            duration=self.speed_profiler.linear_speed_profile.get_total_duration(delta_distance),
            distance=delta_distance,
        )

    def plan_trajectory(self, path: list[OrientedPoint], **kwargs) -> None:
        # Initialize the segment mapper
        segments: list[BaseSegment] = []
        for i in range(len(path) - 1):
            start = path[i]
            target = path[i + 1]

            # 1. Compute the rotation segment
            segments.append(
                self._compute_rotation_segment(start, target)
            )

            # 2. Compute the straight segment
            segments.append(
                self._compute_straight_segment(start, target)
            )

            # 3. Add a stop segment to mark a pause between segments
            if self.params.step_sleep_delay > 0:
                segments.append(
                    StopSegment(
                        start_position=target,
                        end_position=target,
                        duration=self.params.step_sleep_delay,
                    )
                )

        self.segments_mapper = SegmentMapper(segments)

    @BaseTrajectoryPlanner._ensure_planning_started
    def get_plan(self, **kwargs) -> TrajectoryPlanCommand:
        # Get the current time elapsed
        time_elapsed = self._get_trajectory_time_elapsed()

        # Get the active segment
        segment, local_time = self.segments_mapper.get_segment_at_time(time_elapsed)

        # If no segment is found -> plan is over -> stop the robot at the end path
        trajectory_plan_command: TrajectoryPlanCommand | None = None
        if segment is None:
            trajectory_plan_command: TrajectoryPlanCommand = TrajectoryPlanCommand.create_stop_command(
                current_position=self.segments_mapper.get_last_segment().end_position
            )

        # If the segment is a rotation segment
        elif isinstance(segment, RotationSegment):
            th_rotation: float = self.speed_profiler.angular_speed_profile.get_distance(
                time_elapsed=local_time,
                distance=segment.rotation
            )

            th_theta = segment.start_position.theta + th_rotation

            trajectory_plan_command: TrajectoryPlanCommand = TrajectoryPlanCommand(
                position=OrientedPoint(
                    segment.start_position.x, segment.start_position.y, th_theta
                ),
                linear_speed=0.0,
                angular_speed=self.speed_profiler.angular_speed_profile.get_speed(local_time)
            )

        # If the segment is a straight segment
        elif isinstance(segment, StraightSegment):
            th_distance: float = self.speed_profiler.linear_speed_profile.get_distance(
                time_elapsed=local_time,
                distance=segment.distance
            )
            th_x = segment.start_position.x + th_distance * cos(segment.start_position.theta)
            th_y = segment.start_position.y + th_distance * sin(segment.start_position.theta)

            trajectory_plan_command: TrajectoryPlanCommand = TrajectoryPlanCommand(
                position=OrientedPoint(
                    th_x, th_y, segment.start_position.theta
                ),
                linear_speed=self.speed_profiler.linear_speed_profile.get_speed(local_time),
                angular_speed=0.0
            )

        # If the segment is a stop segment
        elif isinstance(segment, StopSegment):
            trajectory_plan_command: TrajectoryPlanCommand = TrajectoryPlanCommand.create_stop_command(
                current_position=segment.start_position
            )

        # Save the last call time
        self._last_call_time: float = time_elapsed

        return trajectory_plan_command

    def get_total_duration(self) -> float:
        return self.segments_mapper.cumulative_durations[-1]
