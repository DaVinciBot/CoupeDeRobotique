# ====== Code Summary ======
# This module defines the RotationSegment class, a subclass of BaseSegment,
# used to represent in-place rotational motion.
# It includes metadata such as total rotation angle and rotation direction (sign), in addition to standard segment data.

from geometry import OrientedPoint
from navigation.trajectory_planner.common.segments.base_segment import BaseSegment


class RotationSegment(BaseSegment):
    """Segment representing rotational motion in place."""

    def __init__(
        self,
        start_position: OrientedPoint,
        end_position: OrientedPoint,
        duration: float,
        rotation: float,
        sign: int,
    ) -> None:
        """Initialize a rotation segment with its start and end pose, duration, rotation angle, and direction.

        Args:
            start_position (OrientedPoint): Pose at the beginning of the rotation.
            end_position (OrientedPoint): Pose at the end of the rotation.
            duration (float): Duration of the rotation movement.
            rotation (float): Total angle rotated during this segment.
            sign (int): Direction of rotation (+1 for CCW, -1 for CW).

        """
        super().__init__(start_position, end_position, duration)
        self.rotation: float = rotation  # Total angle of rotation
        self.sign: int = sign  # Direction of rotation
