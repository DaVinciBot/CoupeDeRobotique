# TODO: to implement !

# ====== Code Summary ======
# ...

# ====== Standard Library Imports ======
from typing import List
import math
import numpy as np
from scipy.interpolate import CubicSpline

# ====== Third-party Library Imports ======
from loggerplusplus import Logger

# ====== Internal Project Imports ======
from geometry import OrientedPoint

# ====== Local Project Imports ======
# Structures
from navigation.trajectory_planner.structs import TrajectoryPlanCommand

# Trajectory planner class & parameters
from navigation.trajectory_planner.basic_trajectory_planner.basic_trajectory_planner_params import (
    BasicTrajectoryPlannerParams,
)
from navigation.trajectory_planner.base_trajectory_planner.base_trajectory_planner import (
    BaseTrajectoryPlanner,
)

# Speed profile
from navigation.trajectory_planner.speed_profile import SpeedProfiler

# Segments
from navigation.trajectory_planner.sequential_trajectory_planner.segments import (
    SegmentMapper,
    SmoothSegment,
)


# ====== Sequential Trajectory Planner Class ======
class BasicTrajectoryPlanner(BaseTrajectoryPlanner[BasicTrajectoryPlannerParams]):
    """
    A trajectory planner that splits the path into CurveSegments (one per pair of waypoints)
    and uses 3-phase curves (acceleration, constant speed, deceleration) for linear and
    angular motion.
    """

    def __init__(
        self,
        params: BasicTrajectoryPlannerParams,
        speed_profiler: SpeedProfiler,
        logger: Logger | None = None,
    ) -> None:
        """
        Initialize the sequential trajectory planner with required parameters.

        Args:
            params (SequentialTrajectoryPlannerParams): Planning parameters.
            speed_profiler (SpeedProfiler): Speed profiler to control segment durations.
            logger (Logger | None): Optional logger.
        """
        super().__init__(params, speed_profiler, logger)
        self._segments_mapper: SegmentMapper | None = None

    def plan_trajectory(self, path: list[OrientedPoint]) -> None:
        """
        Build the trajectory plan from a list of waypoints.

        Args:
            path (list[OrientedPoint]): List of oriented points representing the path.
        """
        if len(path) < 2:
            self.logger.warning("Not enough points in path.")
            self._segments_mapper = None
            return

        # 1) Convert the path into s-parameter
        s_values, x_values, y_values = self._compute_s_param(path)
        s_total = s_values[-1]  # total distance

        # 2) Build cubic splines for x(s) and y(s)
        spline_x = CubicSpline(s_values, x_values)  # X(s)
        spline_y = CubicSpline(s_values, y_values)  # Y(s)

        # 3) Define K sub-intervals in [0..S_total]
        k = self._determine_num_segments(path)
        s_breaks = np.linspace(0, s_total, k + 1)  # shape (K+1,)

        segments = []
        previous_speed = 0.0  # Initial speed for the first segment

        # For each sub-interval, we sample M_k points => sub_spline
        for i in range(k):
            s_start = s_breaks[i]
            s_end = s_breaks[i + 1]

            # Number of sample points for this sub-interval
            num_samples = max(2, self.params.spline_resolution // k)

            # Sample [s_start..s_end]
            sampled_points = self._sample_spline_portion(
                spline_x, spline_y, s_start, s_end, num_samples
            )
            actual_sub_distance = self._compute_total_distance(sampled_points)

            # Determine the speed profile for this segment
            # The departure speed is the previous segment's arrival speed
            departure_speed = previous_speed

            # Check if this is the last segment
            if i == k - 1:
                # For the last segment, set arrival speed to 0.0 (stop)
                arrival_speed = 0.0
            else:
                # Calculate the arrival speed intelligently based on constraints
                arrival_speed = self._compute_arrival_speed(
                    departure_speed, actual_sub_distance
                )

            # Duration from the speed profile
            seg_duration = self.speed_profiler.linear_speed_profile.get_total_duration(
                distance=actual_sub_distance,
                departure_speed=departure_speed,
                arrival_speed=arrival_speed,
            )

            # Build a segment
            seg = SmoothSegment(
                start_position=sampled_points[0],
                end_position=sampled_points[-1],
                duration=seg_duration,
                sampled_points=sampled_points,
                total_distance=actual_sub_distance,
            )
            segments.append(seg)

            # Update the previous speed for the next segment
            previous_speed = arrival_speed

        self._segments_mapper = SegmentMapper(segments)

    @BaseTrajectoryPlanner._ensure_planning_started
    def get_plan(self) -> TrajectoryPlanCommand:
        """
        Retrieve the current motion command based on elapsed time.

        Returns:
            TrajectoryPlanCommand: The motion command for the current time.
        """
        if not self._segments_mapper:
            return TrajectoryPlanCommand.create_stop_command(OrientedPoint(0, 0, 0))

        time_elapsed = self._get_trajectory_time_elapsed()
        segment, local_time = self._segments_mapper.get_segment_at_time(time_elapsed)

        if segment is None:
            # end of trajectory
            last_seg = self._segments_mapper.get_last_segment()
            return TrajectoryPlanCommand.create_stop_command(last_seg.end_position)

        # dist traveled in the current segment
        dist_traveled = self.speed_profiler.linear_speed_profile.get_distance(
            time_elapsed=local_time,
            distance=segment.total_distance,
            departure_speed=0.0,
            arrival_speed=0.0,
        )
        # ratio
        ratio = 0.0
        if segment.total_distance > 1e-9:
            ratio = dist_traveled / segment.total_distance

        # Interpolate
        current_pose = self._interpolate_pose(segment.sampled_points, ratio)

        # linear speed
        v_lin = self.speed_profiler.linear_speed_profile.get_speed(
            time_elapsed=local_time,
            distance=segment.total_distance,
            departure_speed=0.0,
            arrival_speed=0.0,
        )
        # angular speed
        v_ang = self.speed_profiler.angular_speed_profile.get_speed(
            time_elapsed=local_time,
            distance=segment.total_distance,
            departure_speed=0.0,
            arrival_speed=0.0,
        )

        return TrajectoryPlanCommand(
            position=current_pose, linear_speed=v_lin, angular_speed=v_ang
        )

    def get_total_duration(self) -> float:
        """
        Get the total planned duration of the trajectory.

        Returns:
            float: Total duration of the full trajectory.
        """
        if not self._segments_mapper or len(self._segments_mapper.segments) == 0:
            return 0.0
        return self._segments_mapper.cumulative_durations[-1]

    def _compute_s_param(self, path: List[OrientedPoint]):
        """
        Build a param 's' in [0..S_total], plus X, Y arrays for the waypoints.
        """
        s_vals = [0.0]
        x_vals = [path[0].x]
        y_vals = [path[0].y]
        dist_acc = 0.0
        for i in range(1, len(path)):
            dx = path[i].x - path[i - 1].x
            dy = path[i].y - path[i - 1].y
            segdist = math.hypot(dx, dy)
            dist_acc += segdist
            s_vals.append(dist_acc)
            x_vals.append(path[i].x)
            y_vals.append(path[i].y)

        return np.array(s_vals), np.array(x_vals), np.array(y_vals)

    def _sample_spline_portion(
        self,
        spline_x: CubicSpline,
        spline_y: CubicSpline,
        s_start: float,
        s_end: float,
        num_samples: int,
    ) -> List[OrientedPoint]:
        """
        Sample num_samples points in [s_start..s_end].
        """
        num_samples = max(num_samples, 2)

        s_range = np.linspace(s_start, s_end, num_samples)
        points = []
        for s_val in s_range:
            x_val = spline_x(s_val)
            y_val = spline_y(s_val)
            dx = spline_x.derivative()(s_val)
            dy = spline_y.derivative()(s_val)
            theta = math.atan2(dy, dx) if (abs(dx) > 1e-9 or abs(dy) > 1e-9) else 0.0
            points.append(OrientedPoint(x_val, y_val, theta))
        return points

    def _compute_total_distance(self, points: List[OrientedPoint]) -> float:
        """
        Compute total path length from consecutive points.
        """
        dist_acc = 0.0
        for i in range(len(points) - 1):
            dist_acc += points[i].distance(points[i + 1])
        return dist_acc

    def _compute_arrival_speed(self, departure_speed: float, distance: float) -> float:
        """
        Compute the arrival speed for a segment based on the departure speed,
        distance, and constraints.

        Args:
            departure_speed (float): Speed at the start of the segment.
            distance (float): Distance of the segment.

        Returns:
            float: Speed at the end of the segment.
        """
        return self.speed_profiler.linear_speed_profile.get_speed(
            time_elapsed=500, distance=100, arrival_speed=1000
        )
        max_speed = self.speed_profiler.linear_speed_profile.max_speed

        max_acceleration = self.params.max_acceleration

        # Compute the maximum possible arrival speed based on acceleration
        max_possible_speed = math.sqrt(
            departure_speed**2 + 2 * max_acceleration * distance
        )

        # Limit the arrival speed to the maximum allowed speed
        return min(max_speed, max_possible_speed)

    def _interpolate_pose(
        self, points: List[OrientedPoint], ratio: float
    ) -> OrientedPoint:
        """
        Return pose at fraction 'ratio' in [0..1] along 'points'.
        We do a linear search & interpolation. For better efficiency,
        we might keep a cumulative-dist array and do a binary search.
        """
        if ratio <= 0:
            return points[0]
        if ratio >= 1:
            return points[-1]

        total_dist = self._compute_total_distance(points)
        target_d = ratio * total_dist
        acc = 0.0
        for i in range(len(points) - 1):
            segd = points[i].distance(points[i + 1])
            if acc + segd >= target_d:
                frac = (target_d - acc) / segd if segd > 1e-9 else 0.0
                x = points[i].x + frac * (points[i + 1].x - points[i].x)
                y = points[i].y + frac * (points[i + 1].y - points[i].y)
                th = points[i].theta + frac * (points[i + 1].theta - points[i].theta)
                return OrientedPoint(x, y, th)
            acc += segd
        return points[-1]

    def _determine_num_segments(self, path: List[OrientedPoint]) -> int:
        """
        Determine the number of segments (K) based on the path's length and complexity.

        Args:
            path (List[OrientedPoint]): List of oriented points representing the path.

        Returns:
            int: Number of segments (K).
        """
        # Minimum number of segments
        min_segments = 3
        max_segments = 20  # Arbitrary upper limit to avoid excessive segmentation

        # Compute total path length
        total_length = self._compute_total_distance(path)

        # Heuristic: Base number of segments on total length
        length_based_segments = max(
            min_segments, int(total_length / self.params.segment_length_threshold)
        )

        # Compute path complexity (based on changes in direction)
        complexity_score = 0.0
        for i in range(1, len(path) - 1):
            v1 = np.array([path[i].x - path[i - 1].x, path[i].y - path[i - 1].y])
            v2 = np.array([path[i + 1].x - path[i].x, path[i + 1].y - path[i].y])
            if np.linalg.norm(v1) > 1e-9 and np.linalg.norm(v2) > 1e-9:
                angle = np.arccos(
                    np.clip(
                        np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)),
                        -1.0,
                        1.0,
                    )
                )
                complexity_score += angle

        # Heuristic: Add segments based on complexity
        complexity_based_segments = max(
            min_segments, int(complexity_score / self.params.complexity_threshold)
        )

        # Combine both heuristics
        num_segments = min(
            max_segments, max(length_based_segments, complexity_based_segments)
        )
        return num_segments
