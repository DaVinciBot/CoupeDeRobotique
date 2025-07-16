# ====== Code Summary ======
# This module defines the StopSegment class, a subclass of BaseSegment, representing a stationary segment in a trajectory.
# It captures a period of pause or no movement between two poses over a specific duration.

from geometry import OrientedPoint
from navigation.trajectory_planner.common.segments.base_segment import BaseSegment


class StopSegment(BaseSegment):
    """Segment representing a stop or pause in the trajectory.

    Inherits from:
        BaseSegment: The base class representing general trajectory segment attributes.

    Typically used when the robot or agent is stationary for a defined period of time.
    """

    def __init__(
        self,
        start_position: OrientedPoint,
        end_position: OrientedPoint,
        duration: float,
    ) -> None:
        """Initialize a stationary segment with given start and end positions and duration.

        Args:
            start_position (OrientedPoint): Start pose of the stationary segment.
            end_position (OrientedPoint): End pose of the stationary segment (may be identical to start).
            duration (float): Duration of the stop or pause.
        """
        super().__init__(start_position, end_position, duration)
