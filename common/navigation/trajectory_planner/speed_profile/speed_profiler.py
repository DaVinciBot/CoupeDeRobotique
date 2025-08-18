"""Container for linear and angular speed profiles."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from navigation.trajectory_planner.speed_profile.base_speed_profile import (
        BaseSpeedProfile,
    )


@dataclass
class SpeedProfiler:
    """Aggregates linear and angular speed profiles for use in trajectory planning.

    Attributes:
        linear_speed_profile (BaseSpeedProfile): Speed profile used for linear motion.
        angular_speed_profile (BaseSpeedProfile):
            Speed profile used for rotational motion.

    """

    linear_speed_profile: BaseSpeedProfile
    angular_speed_profile: BaseSpeedProfile
