# ====== Code Summary ======
# This module defines the SegmentMapper class, which maps a global time value to its corresponding trajectory segment
# and computes the local time within that segment. It uses cumulative durations and binary search for efficient lookup.
# The class supports retrieving a segment by time and accessing the last segment.

import bisect

from navigation.trajectory_planner.common.segments.base_segment import BaseSegment


class SegmentMapper:
    """Maps trajectory segments to elapsed time using cumulative durations.

    Provides fast segment lookup using binary search.

    """

    def __init__(self, segments: list[BaseSegment]) -> None:
        """Initialize the SegmentMapper with a list of segments and compute cumulative durations.

        Args:
            segments (list[BaseSegment]): List of trajectory segments to be managed.

        """
        self.segments = segments
        self.cumulative_durations: list[float] = []
        cumulative = 0.0

        # Compute the cumulative end times for each segment
        for segment in segments:
            cumulative += segment.duration
            self.cumulative_durations.append(cumulative)

    def _get_previous_cumulative(self, index: int) -> float:
        """Helper method to get the previous cumulative duration.

        Args:
            index (int): Index of the current segment.

        Returns:
            float: Cumulative time before the given index.

        """
        return self.cumulative_durations[index - 1] if index > 0 else 0.0

    def get_segment_at_time(self, t: float) -> tuple[BaseSegment | None, float | None]:
        """Given an overall time t, returns the active segment and local time within that segment.

        Args:
            t (float): Overall elapsed time.

        Returns:
            tuple[BaseSegment | None, float | None]: Tuple containing the segment and the local time within it. Returns (None, None) if t is out of valid bounds.

        """
        if t < 0:
            return None, None

        # Binary search to find the right segment index
        index = bisect.bisect_right(self.cumulative_durations, t)

        if index == len(self.segments):
            return None, None

        previous_cumulative = self._get_previous_cumulative(index)
        local_time = t - previous_cumulative

        return self.segments[index], local_time

    def get_last_segment(self) -> BaseSegment:
        """Retrieve the last segment in the trajectory.

        Returns:
            BaseSegment: The last trajectory segment in the list.

        """
        return self.segments[-1]
