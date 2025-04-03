# ====== Code Summary ======
# This module defines a SequentialTrajectoryPlanner that decomposes a given path of oriented waypoints
# into a sequence of trajectory segments: rotations, straight-line motions, and stops. It uses a
# SpeedProfiler to time and control each segment and constructs a full trajectory that a robot can
# follow sequentially. The planner maps the trajectory to time and returns motion commands for execution.

# ====== Standard Library Imports ======
import math

# ====== Third-party Library Imports ======
from loggerplusplus import Logger

# ====== Internal Project Imports ======
from geometry import OrientedPoint

# ====== Local Project Imports ======
# Structures
from navigation.trajectory_planner.structs import TrajectoryPlanCommand

# Trajectory planner class & parameters
from navigation.trajectory_planner.sequential_trajectory_planner.sequential_trajectory_planner_params import \
    SequentialTrajectoryPlannerParams
from navigation.trajectory_planner.base_trajectory_planner.base_trajectory_planner import BaseTrajectoryPlanner

# Speed profile
from navigation.trajectory_planner.speed_profile import SpeedProfiler

# Segments
from navigation.trajectory_planner.sequential_trajectory_planner.segments import (
    BaseSegment, StraightSegment, RotationSegment, StopSegment, SegmentMapper
)


# ====== Sequential Trajectory Planner Class ======
class SequentialTrajectoryPlanner(BaseTrajectoryPlanner[SequentialTrajectoryPlannerParams]):
    """
    Planner that constructs a sequential series of trajectory segments (rotate, move straight, rotate, stop)
    from a path of oriented points. Supports time-based segment retrieval to provide motion commands.
    """

    def __init__(
            self,
            params: SequentialTrajectoryPlannerParams,
            speed_profiler: SpeedProfiler,
            logger: Logger | None = None
    ) -> None:
        """
        Initialize the sequential trajectory planner with required parameters.

        Args:
            params (SequentialTrajectoryPlannerParams): Planning parameters.
            speed_profiler (SpeedProfiler): Speed profiler to control segment durations.
            logger (Logger | None): Optional logger.
        """
        super().__init__(params, speed_profiler, logger)
        self.segments_mapper: SegmentMapper | None = None
        self._last_call_time: float = 0.0

    def _compute_rotation_segment_to_be_front(self, start: OrientedPoint, target: OrientedPoint) -> RotationSegment:
        """
        Compute rotation needed to face the direction of the next waypoint.

        Args:
            start (OrientedPoint): Current pose.
            target (OrientedPoint): Target waypoint.

        Returns:
            RotationSegment: Segment that rotates in place to face the target.
        """
        # Compute delta-theta to rotate in front of the target
        d_theta = math.atan2(target.y - start.y, target.x - start.x) - start.theta

        # Compute intermediate target position (start + rotation)
        target = OrientedPoint(
            start.x, start.y,
            start.theta + d_theta
        )

        return RotationSegment(
            start_position=start,
            end_position=target,
            duration=self.speed_profiler.angular_speed_profile.get_total_duration(abs(d_theta)),
            rotation=abs(d_theta),
            sign=1 if d_theta > 0 else -1
        )

    def _compute_rotation_segment_to_get_same_orientation(self, start: OrientedPoint, target: OrientedPoint) \
            -> RotationSegment:
        """
        Compute rotation needed to align final orientation with target.

        Args:
            start (OrientedPoint): Current pose after straight segment.
            target (OrientedPoint): Target pose with desired final orientation.

        Returns:
            RotationSegment: Segment that aligns orientation with target.
        """
        # Compute delta-theta to rotate in front of the target
        d_theta = target.theta - start.theta

        # Compute intermediate target position (start + rotation)
        target = OrientedPoint(
            start.x, start.y,
            target.theta
        )

        return RotationSegment(
            start_position=start,
            end_position=target,
            duration=self.speed_profiler.angular_speed_profile.get_total_duration(abs(d_theta)),
            rotation=abs(d_theta),
            sign=1 if d_theta > 0 else -1
        )

    def _compute_straight_segment(self, start: OrientedPoint, target: OrientedPoint) -> StraightSegment:
        """
        Compute straight segment needed to reach the next waypoint.

        Args:
            start (OrientedPoint): Start pose after initial rotation.
            target (OrientedPoint): Target waypoint.

        Returns:
            StraightSegment: Segment that moves in a straight line.
        """
        # Compute delta-distance
        delta_distance = start.distance(target)  # Use shapely method for more performance

        # Compute intermediate target position (start + distance)
        target = OrientedPoint(
            target.x, target.y,
            start.theta
        )

        return StraightSegment(
            start_position=start,
            end_position=target,
            duration=self.speed_profiler.linear_speed_profile.get_total_duration(delta_distance),
            distance=delta_distance,
        )

    def plan_trajectory(self, path: list[OrientedPoint], **kwargs) -> None:
        """
        Build trajectory plan from a list of waypoints.

        Args:
            path (list[OrientedPoint]): List of oriented points representing the path.
        """
        # Initialize the segment mapper
        segments: list[BaseSegment] = []
        for i in range(len(path) - 1):
            start = path[i]
            target = path[i + 1]

            # 1. Compute the rotation segment (get orientation in front of the target)
            rotation_segment: RotationSegment = self._compute_rotation_segment_to_be_front(start, target)
            segments.append(rotation_segment)

            # 2. Compute the straight segment (move to the target)
            straight_segment: StraightSegment = self._compute_straight_segment(rotation_segment.end_position, target)
            segments.append(straight_segment)

            # 3. Compute the rotation segment (get orientation of the target point)
            rotation_segment: RotationSegment = self._compute_rotation_segment_to_get_same_orientation(
                straight_segment.end_position, target
            )
            segments.append(rotation_segment)

            # 4. Add a stop segment to mark a pause between segments
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
        """
        Retrieve the current motion command based on elapsed time.

        Returns:
            TrajectoryPlanCommand: The motion command for the current time.
        """
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
                distance=segment.rotation  # IMPORTANT: Use distance parameter to get the th rotation
            )

            th_theta = segment.start_position.theta + th_rotation * segment.sign

            trajectory_plan_command: TrajectoryPlanCommand = TrajectoryPlanCommand(
                position=OrientedPoint(
                    segment.start_position.x, segment.start_position.y, th_theta
                ),
                linear_speed=0.0,
                angular_speed=self.speed_profiler.angular_speed_profile.get_speed(
                    time_elapsed=local_time,
                    distance=segment.rotation  # IMPORTANT: Use distance parameter to get the th speed
                ),
            )

        # If the segment is a straight segment
        elif isinstance(segment, StraightSegment):
            th_distance: float = self.speed_profiler.linear_speed_profile.get_distance(
                time_elapsed=local_time,
                distance=segment.distance  # IMPORTANT: Use distance parameter to get the th distance
            )
            th_x = segment.start_position.x + th_distance * cos(segment.start_position.theta)
            th_y = segment.start_position.y + th_distance * sin(segment.start_position.theta)

            trajectory_plan_command: TrajectoryPlanCommand = TrajectoryPlanCommand(
                position=OrientedPoint(
                    th_x, th_y, segment.start_position.theta
                ),
                linear_speed=self.speed_profiler.linear_speed_profile.get_speed(
                    time_elapsed=local_time,
                    distance=segment.distance  # IMPORTANT: Use distance parameter to get the th speed
                ),
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
        """
        Get the total planned duration of the trajectory.

        Returns:
            float: Total duration of the full trajectory.
        """
        return self.segments_mapper.cumulative_durations[-1]
