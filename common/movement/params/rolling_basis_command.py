from dataclasses import dataclass
from geometry import OrientedPoint


@dataclass
class RollingBasisCommand:
    position: OrientedPoint
    linear_speed: float
    angular_speed: float

    def get_command(self) -> tuple[float, float, OrientedPoint]:
        return self.linear_speed, self.angular_speed, self.position
