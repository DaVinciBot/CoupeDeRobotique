"""Parameters for the null ACS detection profile."""

from __future__ import annotations

from navigation.avoidance.acs_detection_profiles.base_acs_detection_profiles import (
    BaseAcsDetectionProfileParams,
)
from navigation.avoidance.acs_detection_profiles.struct import AcsDetectionProfile


class NoAcsDetectionProfileParams(BaseAcsDetectionProfileParams):
    """Parameters for the no ACS detection profile."""

    def __init__(self, acs_distance: float = 0.0) -> None:
        """Initializes the NoAcsDetectionProfileParams.

        Args:
            acs_distance (float, optional): Distance to the obstacle. Defaults to 0.0.

        """
        super().__init__(
            acs_detection_profile=AcsDetectionProfile.NO,
            acs_distance=acs_distance,
        )
