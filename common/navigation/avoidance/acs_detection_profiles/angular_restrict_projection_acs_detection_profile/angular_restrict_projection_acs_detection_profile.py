"""ACS detection profile using angular restriction to trigger avoidance."""

from math import atan2
from typing import override

from arena import AllyZone, EnemyZone
from navigation.avoidance.acs_detection_profiles import (
    AngularRestrictProjectionAcsDetectionProfileParams,
    BaseAcsDetectionProfile,
)


class AngularRestrictProjectionAcsDetectionProfile(
    BaseAcsDetectionProfile[AngularRestrictProjectionAcsDetectionProfileParams],
):
    """Angular restrict projection ACS detection profile."""

    def __init__(
        self,
        params: AngularRestrictProjectionAcsDetectionProfileParams,
    ) -> None:
        """Initializes the AngularRestrictProjectionAcsDetectionProfile.

        Args:
            params (AngularRestrictProjectionAcsDetectionProfileParams):
                Parameters for the angular restrict projection ACS detection profile.

        """
        super().__init__(params)

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
