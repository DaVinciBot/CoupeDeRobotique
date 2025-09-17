"""Base segment primitive for trajectory planning."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from geometry import OrientedPoint


class BaseSegment:
    """Base class for all motion segments."""

    def __init__(
        self,
        start_position: OrientedPoint,
        end_position: OrientedPoint,
        duration: float,
    ) -> None:
        """Initialize the base segment with essential trajectory information.

        Args:
            start_position (OrientedPoint): Starting pose of the motion segment.
            end_position (OrientedPoint): Ending pose of the motion segment.
            duration (float): Duration of the segment's movement or action.
        """
        self.start_position: OrientedPoint = (
            start_position  # Pose at the beginning of the segment
        )
        self.end_position: OrientedPoint = (
            end_position  # Pose at the end of the segment
        )
        self.duration: float = duration  # Time duration of the segment
