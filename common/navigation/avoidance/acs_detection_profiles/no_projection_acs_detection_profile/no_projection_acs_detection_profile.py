"""No Projection ACS Detection Profile Module."""

from __future__ import annotations

from typing import TYPE_CHECKING, override

from navigation.avoidance.acs_detection_profiles.base_acs_detection_profiles import (
    BaseAcsDetectionProfile,
)
from navigation.avoidance.acs_detection_profiles.no_projection_acs_detection_profile.no_projection_acs_detection_profile_params import (  # noqa: E501
    NoProjectionAcsDetectionProfileParams,
)

if TYPE_CHECKING:
    from arena.base_arena.arena_zones import AllyZone, EnemyZone


class NoProjectionAcsDetectionProfile(
    BaseAcsDetectionProfile[NoProjectionAcsDetectionProfileParams],
):
    """No projection ACS detection profile."""

    @override
    def is_acs_triggered(self, ally_zone: AllyZone, enemy_zone: EnemyZone) -> bool:
        """Checks if the ACS is triggered based on the ally and enemy zones.

        Args:
            ally_zone (AllyZone): The ally zone information.
            enemy_zone (EnemyZone): The enemy zone information.

        Returns:
            bool: ``True`` if the ACS is triggered, ``False`` otherwise.
        """
        distance = ally_zone.point.distance(enemy_zone.point)
        if distance <= self.params.acs_distance:
            self._logger.debug(f"[NAV:ACS] Triggered - distance: {distance:.1f}cm")
            return True
        return False
