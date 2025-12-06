"""Parameter container for the speed ACS profile."""

from __future__ import annotations

from navigation.avoidance.acs_detection_profiles.base_acs_detection_profiles import (
    BaseAcsDetectionProfileParams,
)
from navigation.avoidance.acs_detection_profiles.struct import AcsDetectionProfile


class SpeedAcsDetectionProfileParams(BaseAcsDetectionProfileParams):
    """Parameters for the speed ACS detection profile."""

    def __init__(self, acs_distance: float, reaction_time: float, horizon: float, ) -> None:
        """
        Initialize SpeedAcsDetectionProfileParams.
        Args:
            acs_distance (float): Minimum safe distance to maintain from other robots.
            reaction_time (float): Time delay before reacting to detected obstacles.
            horizon (float): Time horizon to consider for potential collisions.
        """
        self.acs_distance = acs_distance
        self.reaction_time = reaction_time
        self.horizon = horizon

        super().__init__(
            acs_detection_profile=AcsDetectionProfile.SPEED,
            acs_distance=self.acs_distance,
        )
