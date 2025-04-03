import bisect
from geometry import OrientedPoint


class BaseSegment:
    def __init__(
            self,
            start_position: OrientedPoint, end_position: OrientedPoint,
            duration: float
    ):
        self.start_position: OrientedPoint = start_position
        self.end_position: OrientedPoint = end_position
        self.duration: float = duration


class StraightSegment(BaseSegment):

    def __init__(
            self,
            start_position: OrientedPoint, end_position: OrientedPoint,
            duration: float,
            distance: float
    ):
        super().__init__(start_position, end_position, duration)
        self.distance: float = distance


class RotationSegment(BaseSegment):
    def __init__(
            self,
            start_position: OrientedPoint, end_position: OrientedPoint,
            duration: float,
            rotation: float,
            sign: int
    ):
        super().__init__(start_position, end_position, duration)
        self.rotation: float = rotation
        self.sign: int = sign


class StopSegment(BaseSegment):
    def __init__(
            self,
            start_position: OrientedPoint, end_position: OrientedPoint,
            duration: float
    ):
        super().__init__(start_position, end_position, duration)


class SegmentMapper:
    def __init__(self, segments: list[BaseSegment]):
        """
        Initializes the mapper with a list of segments, each having a 'duration' attribute.
        Precomputes a cumulative duration list for fast lookup.

        Args:
            segments (list): List of segment objects, each with a 'duration' attribute.
        """
        self.segments = segments
        self.cumulative_durations = []
        cumulative = 0.0
        for segment in segments:
            cumulative += segment.duration
            self.cumulative_durations.append(cumulative)

    def get_segment_at_time(self, t: float):
        """
        Given an overall time t, returns a tuple (segment, local_time) where:
          - 'segment' is the segment active at time t,
          - 'local_time' is the offset time within that segment.

        This method uses binary search for an O(log n) lookup.

        Args:
            t (float): The overall time instant.

        Returns:
            tuple: (segment, local_time) if found, otherwise (None, None) if t is negative or exceeds total duration.
        """
        if t < 0:
            return None, None

        # Find the index using binary search in the cumulative durations list.
        index = bisect.bisect_right(self.cumulative_durations, t)

        # If the time exceeds the total duration, return (None, None)
        if index == len(self.segments):
            return None, None

        # Calculate the local time within the found segment.
        previous_cumulative = self.cumulative_durations[index - 1] if index > 0 else 0.0
        local_time = t - previous_cumulative
        return self.segments[index], local_time

    def get_last_segment(self):
        """
        Returns the last segment in the list.
        """
        return self.segments[-1]
