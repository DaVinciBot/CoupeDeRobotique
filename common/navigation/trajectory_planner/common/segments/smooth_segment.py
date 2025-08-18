"""Curved trajectory segment built from sampled points."""

from __future__ import annotations

from typing import TYPE_CHECKING

from navigation.trajectory_planner.common.segments.base_segment import BaseSegment

if TYPE_CHECKING:
    from geometry import OrientedPoint


class SmoothSegment(BaseSegment):
    """A segment representing a curved trajectory."""

    def __init__(
        self,
        start_position: OrientedPoint,
        end_position: OrientedPoint,
        duration: float,
        sampled_points: list[OrientedPoint],
        total_distance: float,
    ) -> None:
        """Create a curved trajectory segment.

        Args:
            start_position (OrientedPoint): Start pose of the segment.
            end_position (OrientedPoint): End pose of the segment.
            duration (float): Duration of the segment.
            sampled_points (list[OrientedPoint]):
                Points sampled along the trajectory for interpolation or visualization.
            total_distance (float): The total traveled distance of this segment.

        """
        super().__init__(start_position, end_position, duration)
        self.sampled_points = (
            sampled_points  # Holds the trajectory's intermediate points
        )
        self.total_distance = total_distance  # Represents the length of the curved path
