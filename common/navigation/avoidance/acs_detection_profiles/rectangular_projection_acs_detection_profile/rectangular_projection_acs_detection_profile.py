"""ACS detection profile based on a rectangular projection ahead of the robot."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, override

from geometry import Polygon, rotate, translate
from navigation.avoidance.acs_detection_profiles.base_acs_detection_profiles import (
    BaseAcsDetectionProfile,
)
from navigation.avoidance.acs_detection_profiles.rectangular_projection_acs_detection_profile.rectangular_projection_acs_detection_profile_params import (  # noqa: E501
    RectangularProjectionAcsDetectionProfileParams,
)

if TYPE_CHECKING:
    from arena.base_arena.arena_zones import AllyZone, EnemyZone


class RectangularProjectionAcsDetectionProfile(
    BaseAcsDetectionProfile[RectangularProjectionAcsDetectionProfileParams],
):
    """Rectangular projection ACS detection profile."""

    def _create_rectangular_projection(self, ally_zone: AllyZone) -> Polygon:
        """Creates a rectangular projection polygon based on the ally zone.

        Args:
            ally_zone (AllyZone): The ally zone to base the projection on.

        Returns:
            Polygon: The rectangular projection polygon.

        Raises:
            ValueError: If `ally_zone.point.theta` is None.
        """
        if ally_zone.point.theta is None:
            msg = "ally_zone.point.theta must be defined."
            raise ValueError(msg)
        rectangle = Polygon(
            [
                (-self.params.half_length_view, -self.params.half_width_view),
                (+self.params.half_length_view, -self.params.half_width_view),
                (+self.params.half_length_view, +self.params.half_width_view),
                (-self.params.half_length_view, +self.params.half_width_view),
            ],
        )
        rotated_rectangle: Polygon = rotate(
            rectangle,
            ally_zone.point.theta,
            origin=(0, 0),
            use_radians=True,
        )

        dx = ally_zone.point.x + self.params.half_length_view * math.cos(
            ally_zone.point.theta,
        )
        dy = ally_zone.point.y + self.params.half_length_view * math.sin(
            ally_zone.point.theta,
        )
        return translate(rotated_rectangle, xoff=dx, yoff=dy)

    @override
    def is_acs_triggered(self, ally_zone: AllyZone, enemy_zone: EnemyZone) -> bool:
        """Determine if the anti-collision system should engage.

        Args:
            ally_zone (AllyZone): The robot's current zone.
            enemy_zone (EnemyZone): The detected enemy zone.

        Returns:
            bool: ``True`` if avoidance should be triggered, ``False`` otherwise.
        """
        projection = self._create_rectangular_projection(ally_zone)
        if projection.contains(enemy_zone.point):
            distance = ally_zone.point.distance(enemy_zone.point)
            self.logger.info(
                f"ACS triggered. Distance: {distance}",
            )
            return True
        return False
