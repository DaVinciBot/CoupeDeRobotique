"""Trajectory segment representing a pause in motion."""

from __future__ import annotations

from typing import TYPE_CHECKING

from navigation.trajectory_planner.common.segments.base_segment import BaseSegment

if TYPE_CHECKING:
    from geometry import OrientedPoint


class StopSegment(BaseSegment):
    """Segment representing a stop or pause in the trajectory."""

    def __init__(
        self,
        start_position: OrientedPoint,
        end_position: OrientedPoint,
        duration: float,
    ) -> None:
        """Initialize a stationary segment.

        Args:
            start_position (OrientedPoint): Start pose of the stationary segment.
            end_position (OrientedPoint):
                End pose of the stationary segment (may be identical to start).
            duration (float): Duration of the stop or pause.

        """
        super().__init__(start_position, end_position, duration)
