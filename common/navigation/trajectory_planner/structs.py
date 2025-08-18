"""Container for linear and angular speed profiles."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from geometry import OrientedPoint


class TrajectoryPlannerStrategy(Enum):
    """Enumeration of available trajectory planner strategies.

    Attributes:
        BASIC: Use basic trajectory planner.
        SEQUENTIAL: Use sequential trajectory planner.

    """

    BASIC = auto()
    """Use basic trajectory planner."""
    SEQUENTIAL = auto()
    """Use sequential trajectory planner."""


@dataclass
class TrajectoryPlanCommand:
    """Represents a motion command in the trajectory plan.

    Attributes:
        position (OrientedPoint): Target pose of the robot.
        linear_speed (float): Linear velocity component.
        angular_speed (float): Angular velocity component.

    """

    position: OrientedPoint
    """Target pose of the robot."""
    linear_speed: float
    """Linear velocity component."""
    angular_speed: float
    """Angular velocity component."""

    @classmethod
    def create_stop_command(
        cls,
        current_position: OrientedPoint,
    ) -> TrajectoryPlanCommand:
        """Create a stop command that holds ``current_position``.

        Args:
            current_position (OrientedPoint): Current pose to hold.

        Returns:
            TrajectoryPlanCommand: Stop command.

        """
        return cls(
            position=current_position,
            linear_speed=0.0,
            angular_speed=0.0,
        )

    def get_full_command(self) -> tuple[float, float, OrientedPoint]:
        """Return ``(linear_speed, angular_speed, position)``.

        Returns:
            tuple[float, float, OrientedPoint]:
                Tuple containing ``linear_speed``, ``angular_speed`` and
                ``position``.

        """
        return self.linear_speed, self.angular_speed, self.position

    def get_position_command(self) -> OrientedPoint:
        """Retrieve the target position.

        Returns:
            OrientedPoint: The target position of the robot.

        """
        return self.position
