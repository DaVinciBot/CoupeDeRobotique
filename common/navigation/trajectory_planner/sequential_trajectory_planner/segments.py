# ====== Code Summary ======
# This module defines trajectory segment classes and a segment manager called `SegmentMapper`.
# Each segment type represents a specific motion: straight line, rotation, or stop.
# The `SegmentMapper` allows efficient retrieval of the current segment and local time at any
# point during trajectory execution using cumulative duration indexing and binary search.

# ====== Standard Library Imports ======
import bisect
from typing import List

# ====== Internal Project Imports ======
from geometry import OrientedPoint


class BaseSegment:
    """
    Base class for all motion segments.

    Attributes:
        start_position (OrientedPoint): Start pose of the segment.
        end_position (OrientedPoint): End pose of the segment.
        duration (float): Duration of the segment.
    """

    def __init__(
        self,
        start_position: OrientedPoint,
        end_position: OrientedPoint,
        duration: float,
    ):
        self.start_position: OrientedPoint = start_position
        self.end_position: OrientedPoint = end_position
        self.duration: float = duration


class StraightSegment(BaseSegment):
    """
    Segment representing straight-line motion.

    Attributes:
        distance (float): Distance to be covered during the segment.
    """

    def __init__(
        self,
        start_position: OrientedPoint,
        end_position: OrientedPoint,
        duration: float,
        distance: float,
    ):
        super().__init__(start_position, end_position, duration)
        self.distance: float = distance


class RotationSegment(BaseSegment):
    """
    Segment representing rotational motion in place.

    Attributes:
        rotation (float): Total angle to rotate.
        sign (int): Direction of rotation (+1 for CCW, -1 for CW).
    """

    def __init__(
        self,
        start_position: OrientedPoint,
        end_position: OrientedPoint,
        duration: float,
        rotation: float,
        sign: int,
    ):
        super().__init__(start_position, end_position, duration)
        self.rotation: float = rotation
        self.sign: int = sign


class StopSegment(BaseSegment):
    """
    Segment representing a stop or pause in the trajectory.
    """

    def __init__(
        self,
        start_position: OrientedPoint,
        end_position: OrientedPoint,
        duration: float,
    ):
        super().__init__(start_position, end_position, duration)


class SmoothSegment(BaseSegment):
    """
    A segment representing a curved trajectory.
    """

    def __init__(
        self,
        start_position: OrientedPoint,
        end_position: OrientedPoint,
        duration: float,
        sampled_points: List[OrientedPoint],
        total_distance: float,
    ):
        """
        Create a segment representing a curved trajectory.

            Args:
                start_position (OrientedPoint): Start pose of the segment.
                end_position (OrientedPoint): End pose of the segment.
                duration (float): Duration of the segment.
                sampled_points (List[OrientedPoint]): List of points sampled along the trajectory.
                total_distance (float): Total distance of the trajectory.
        """
        super().__init__(start_position, end_position, duration)
        self.sampled_points = sampled_points
        self.total_distance = total_distance


class SegmentMapper:
    """
    Maps trajectory segments to elapsed time using cumulative durations.
    Provides fast segment lookup using binary search.

    Attributes:
        segments (list[BaseSegment]): List of trajectory segments.
        cumulative_durations (list[float]): Cumulative end times of each segment.
    """

    def __init__(self, segments: list[BaseSegment]):
        """
        Initialize the mapper with a list of segments and compute cumulative durations.

        Args:
            segments (list[BaseSegment]): List of trajectory segments.
        """
        self.segments = segments
        self.cumulative_durations = []
        cumulative = 0.0
        for segment in segments:
            cumulative += segment.duration
            self.cumulative_durations.append(cumulative)

    def get_segment_at_time(self, t: float):
        """
        Given an overall time t, returns the active segment and local time within that segment.

        Args:
            t (float): Overall elapsed time.

        Returns:
            tuple[BaseSegment | None, float | None]: (segment, local_time) or (None, None) if t is out of bounds.
        """
        if t < 0:
            return None, None

        index = bisect.bisect_right(self.cumulative_durations, t)

        if index == len(self.segments):
            return None, None

        previous_cumulative = self.cumulative_durations[index - 1] if index > 0 else 0.0
        local_time = t - previous_cumulative
        return self.segments[index], local_time

    def get_last_segment(self) -> BaseSegment:
        """
        Retrieve the last segment in the trajectory.

        Returns:
            BaseSegment: The last trajectory segment.
        """
        return self.segments[-1]
