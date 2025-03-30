from dataclasses import dataclass
from geometry import OrientedPoint


@dataclass
class TrajectoryPlanCommand:
    position: OrientedPoint
    linear_speed: float
    angular_speed: float

    @classmethod
    def create_stop_command(cls, current_position: OrientedPoint) -> "TrajectoryPlanCommand":
        return cls(
            position=current_position,
            linear_speed=0.0,
            angular_speed=0.0,
        )

    def get_command(self) -> tuple[float, float, OrientedPoint]:
        return self.linear_speed, self.angular_speed, self.position
