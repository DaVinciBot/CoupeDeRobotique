from navigation.trajectory_planner.speed_profile.base_speed_profile import BaseSpeedProfile

from dataclasses import dataclass


@dataclass
class SpeedProfiler:
    linear_speed_profile: BaseSpeedProfile
    angular_speed_profile: BaseSpeedProfile
