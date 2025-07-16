# ====== Code Summary ======
# This module defines the SmoothSegment class, a subclass of BaseSegment, representing a curved trajectory segment.
# It encapsulates metadata such as start and end positions, duration, sampled intermediate points, and total distance.

from geometry import OrientedPoint
from navigation.trajectory_planner.common.segments.base_segment import BaseSegment


class SmoothSegment(BaseSegment):
    """A segment representing a curved trajectory.

    Attributes:
        sampled_points (list[OrientedPoint]): List of points sampled along the curved path.
        total_distance (float): Total distance covered by the trajectory.
    """

    def __init__(
        self,
        start_position: OrientedPoint,
        end_position: OrientedPoint,
        duration: float,
        sampled_points: list[OrientedPoint],
        total_distance: float,
    ) -> None:
        """Initialize a curved trajectory segment with its start and end poses, duration,
        sampled path points, and the total distance.

        Args:
            start_position (OrientedPoint): Start pose of the segment.
            end_position (OrientedPoint): End pose of the segment.
            duration (float): Duration of the segment.
            sampled_points (list[OrientedPoint]): Points sampled along the trajectory for interpolation or visualization.
            total_distance (float): The total traveled distance of this segment.
        """
        super().__init__(start_position, end_position, duration)
        self.sampled_points = (
            sampled_points  # Holds the trajectory's intermediate points
        )
        self.total_distance = total_distance  # Represents the length of the curved path
