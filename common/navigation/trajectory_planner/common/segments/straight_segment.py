"""Straight-line trajectory segment."""

from __future__ import annotations

from typing import TYPE_CHECKING

from navigation.trajectory_planner.common.segments.base_segment import BaseSegment

if TYPE_CHECKING:
    from geometry import OrientedPoint


class StraightSegment(BaseSegment):
    """Segment representing straight-line motion."""

    def __init__(
        self,
        start_position: OrientedPoint,
        end_position: OrientedPoint,
        duration: float,
        distance: float,
    ) -> None:
        """Initialize a straight-line motion segment.

        Args:
            start_position (OrientedPoint): Starting pose of the segment.
            end_position (OrientedPoint): Ending pose of the segment.
            duration (float): Duration of the segment motion.
            distance (float): Total distance covered in the segment.
        """
        super().__init__(start_position, end_position, duration)
        self.distance: float = distance  # Length of the straight-line path
