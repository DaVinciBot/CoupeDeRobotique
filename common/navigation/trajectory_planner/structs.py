# ====== Code Summary ======
# This module defines the `TrajectoryPlanCommand` dataclass, which encapsulates a single command
# for a robot's motion. It includes the robot's target position, linear speed, and angular speed.
# It also provides utility methods to create a stop command and retrieve the command as a tuple.

# ====== Standard Library Imports ======
from dataclasses import dataclass
from enum import Enum, auto

# ====== Internal Project Imports ======
from geometry import OrientedPoint


class TrajectoryPlannerStrategy(Enum):
    BASIC = auto()
    SEQUENTIAL = auto()


@dataclass
class TrajectoryPlanCommand:
    """
    Represents a motion command in the trajectory plan.

    Attributes:
        position (OrientedPoint): Target pose of the robot.
        linear_speed (float): Linear velocity component.
        angular_speed (float): Angular velocity component.
    """

    position: OrientedPoint
    linear_speed: float
    angular_speed: float

    @classmethod
    def create_stop_command(
        cls, current_position: OrientedPoint
    ) -> "TrajectoryPlanCommand":
        """
        Create a stop command that holds the robot at the given position with zero speed.

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

    def get_command(self) -> tuple[float, float, OrientedPoint]:
        """
        Retrieve the command as a tuple for control interfaces.

        Returns:
            tuple: (linear_speed, angular_speed, position)
        """
        return self.linear_speed, self.angular_speed, self.position
