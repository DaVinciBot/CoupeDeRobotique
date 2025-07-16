# ====== Code Summary ======
# This module defines the StraightSegment class, a subclass of BaseSegment, representing straight-line motion.
# It stores trajectory data such as start and end positions, duration, and the total distance to be traveled.

from geometry import OrientedPoint
from navigation.trajectory_planner.common.segments.base_segment import BaseSegment


class StraightSegment(BaseSegment):
    """Segment representing straight-line motion.

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
        """Initialize a straight-line motion segment.

        Args:
            start_position (OrientedPoint): Starting pose of the segment.
            end_position (OrientedPoint): Ending pose of the segment.
            duration (float): Duration of the segment motion.
            distance (float): Total distance covered in the segment.
        """
        super().__init__(start_position, end_position, duration)
        self.distance: float = distance  # Length of the straight-line path
