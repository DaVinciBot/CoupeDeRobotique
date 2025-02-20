from dataclasses import dataclass


@dataclass
class SpeedProfile:
    max_linear_speed: float  # Max 10.0 cm/s
    max_angular_speed: float  # Max 6.0 rad/s
    max_linear_acceleration: float  # Max 0.5 cm/s^2
    max_angular_acceleration: float  # Max 1.0 rad/s^2
    max_linear_deceleration: float  # Max 0.5 cm/s^2
    max_angular_deceleration: float  # Max 1.0 rad/s^2
