"""ACS detection profile that never triggers avoidance."""

from __future__ import annotations

from typing import TYPE_CHECKING, override

from navigation.avoidance.acs_detection_profiles.base_acs_detection_profiles import (
    BaseAcsDetectionProfile,
)
from navigation.avoidance.acs_detection_profiles.no_acs_detection_profile.no_acs_detection_profile_params import (  # noqa: E501
    NoAcsDetectionProfileParams,
)

if TYPE_CHECKING:
    from arena import AllyZone, EnemyZone


class NoAcsDetectionProfile(BaseAcsDetectionProfile[NoAcsDetectionProfileParams]):
    """No ACS detection profile."""

    def __init__(self, params: NoAcsDetectionProfileParams) -> None:
        """Initializes the NoAcsDetectionProfile.

        Args:
            params (NoAcsDetectionProfileParams):
                Parameters for the no ACS detection profile.

        """
        super().__init__(params)

    @override
    def is_acs_triggered(self, ally_zone: AllyZone, enemy_zone: EnemyZone) -> bool:
        return False
