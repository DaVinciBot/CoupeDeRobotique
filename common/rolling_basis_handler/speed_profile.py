from dataclasses import dataclass


@dataclass
class SpeedProfile:
    max_linear_speed: float  # Max 10.0 cm/s
    max_angular_speed: float  # Max 6.0 rad/s
    max_linear_acceleration: float  # Max 0.5 cm/s^2
    max_angular_acceleration: float  # Max 1.0 rad/s^2
    max_linear_deceleration: float  # Max 0.5 cm/s^2
    max_angular_deceleration: float  # Max 1.0 rad/s^2

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            max_linear_speed=data["max_linear_speed"],
            max_angular_speed=data["max_angular_speed"],
            max_linear_acceleration=data["max_linear_acceleration"],
            max_angular_acceleration=data["max_angular_acceleration"],
            max_linear_deceleration=data["max_linear_deceleration"],
            max_angular_deceleration=data["max_angular_deceleration"],
        )
