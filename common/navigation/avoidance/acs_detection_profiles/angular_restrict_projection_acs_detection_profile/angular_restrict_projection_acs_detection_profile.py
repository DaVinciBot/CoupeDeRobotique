"""ACS detection profile using angular restriction to trigger avoidance."""

from __future__ import annotations

from math import atan2
from typing import TYPE_CHECKING, override

from navigation.avoidance.acs_detection_profiles.angular_restrict_projection_acs_detection_profile.angular_restrict_projection_acs_detection_profile_params import (  # noqa: E501
    AngularRestrictProjectionAcsDetectionProfileParams,
)
from navigation.avoidance.acs_detection_profiles.base_acs_detection_profiles import (
    BaseAcsDetectionProfile,
)

if TYPE_CHECKING:
    from arena.base_arena import AllyZone, EnemyZone


class AngularRestrictProjectionAcsDetectionProfile(
    BaseAcsDetectionProfile[AngularRestrictProjectionAcsDetectionProfileParams],
):
    """Angular restrict projection ACS detection profile."""

    @override
    def is_acs_triggered(self, ally_zone: AllyZone, enemy_zone: EnemyZone) -> bool:
        """Check if the ACS is triggered.

        Args:
            ally_zone (AllyZone): The ally zone.
            enemy_zone (EnemyZone): The enemy zone.

        Returns:
            bool: ``True`` if the ACS is triggered, ``False`` otherwise.
        """
        angle = (
            atan2(
                enemy_zone.point.y - ally_zone.point.y,
                enemy_zone.point.x - ally_zone.point.x,
            )
            - ally_zone.point.theta
        )
        if abs(angle) <= self.params.half_angle_view:
            distance = ally_zone.point.distance(enemy_zone.point)
            self.logger.info(
                f"ACS triggered. Distance: {distance}",
            )
            return True
        return False
