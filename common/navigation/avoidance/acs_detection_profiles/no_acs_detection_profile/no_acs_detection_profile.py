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
    from arena.base_arena import AllyZone, EnemyZone


class NoAcsDetectionProfile(BaseAcsDetectionProfile[NoAcsDetectionProfileParams]):
    """No ACS detection profile."""

    @override
    def is_acs_triggered(self, ally_zone: AllyZone, enemy_zone: EnemyZone) -> bool:
        """Determine if the anti-collision system should engage.

        Args:
            ally_zone (AllyZone): The robot's current zone.
            enemy_zone (EnemyZone): The detected enemy zone.

        Returns:
            bool: ``True`` if avoidance should be triggered, ``False`` otherwise.
        """
        return False
