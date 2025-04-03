# ====== Code Summary ======
# This module defines the `SpeedProfiler` data class, which groups together
# linear and angular speed profiles used for motion planning. Each profile is
# an implementation of the `BaseSpeedProfile` interface, allowing flexible configuration
# of movement characteristics.

# ====== Standard Library Imports ======
from dataclasses import dataclass

# ====== Internal Project Imports ======
from navigation.trajectory_planner.speed_profile.base_speed_profile import BaseSpeedProfile


@dataclass
class SpeedProfiler:
    """
    Aggregates linear and angular speed profiles for use in trajectory planning.

    Attributes:
        linear_speed_profile (BaseSpeedProfile): Speed profile used for linear motion.
        angular_speed_profile (BaseSpeedProfile): Speed profile used for rotational motion.
    """
    linear_speed_profile: BaseSpeedProfile
    angular_speed_profile: BaseSpeedProfile
