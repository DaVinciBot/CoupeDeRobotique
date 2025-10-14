"""Factory for ACS detection profiles.

This module selects a concrete profile implementation based on parameters.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from navigation.avoidance.acs_detection_profiles.angular_restrict_projection_acs_detection_profile import (  # noqa: E501
    AngularRestrictProjectionAcsDetectionProfile,
    AngularRestrictProjectionAcsDetectionProfileParams,
)
from navigation.avoidance.acs_detection_profiles.no_acs_detection_profile import (
    NoAcsDetectionProfile,
    NoAcsDetectionProfileParams,
)
from navigation.avoidance.acs_detection_profiles.no_projection_acs_detection_profile import (  # noqa: E501
    NoProjectionAcsDetectionProfile,
    NoProjectionAcsDetectionProfileParams,
)
from navigation.avoidance.acs_detection_profiles.rectangular_projection_acs_detection_profile import (  # noqa: E501
    RectangularProjectionAcsDetectionProfile,
    RectangularProjectionAcsDetectionProfileParams,
)
from navigation.avoidance.acs_detection_profiles.struct import AcsDetectionProfile

if TYPE_CHECKING:
    from navigation.avoidance.acs_detection_profiles.base_acs_detection_profiles import (  # noqa: E501
        BaseAcsDetectionProfile,
        BaseAcsDetectionProfileParams,
    )


class AcsDetectionProfileFactory:
    """Instantiate an ACS detection profile for the requested strategy."""

    @staticmethod
    def instantiate(
        params: BaseAcsDetectionProfileParams,
    ) -> BaseAcsDetectionProfile[Any]:
        """Create an ACS detection profile instance based on strategy parameters.

        Args:
            params (BaseAcsDetectionProfileParams):
                Parameters describing the desired profile.

        Returns:
            BaseAcsDetectionProfile[Any]: The instantiated detection profile.

        Raises:
            ValueError: If the avoidance strategy is not supported.
        """
        profile = params.acs_detection_profile

        if profile == AcsDetectionProfile.NO:
            return NoAcsDetectionProfile(cast("NoAcsDetectionProfileParams", params))

        if profile == AcsDetectionProfile.NO_PROJECTION:
            return NoProjectionAcsDetectionProfile(
                cast("NoProjectionAcsDetectionProfileParams", params),
            )

        if profile == AcsDetectionProfile.RECTANGULAR_PROJECTION:
            return RectangularProjectionAcsDetectionProfile(
                cast("RectangularProjectionAcsDetectionProfileParams", params),
            )

        if profile == AcsDetectionProfile.ANGULAR_RESTRICT_PROJECTION:
            return AngularRestrictProjectionAcsDetectionProfile(
                cast("AngularRestrictProjectionAcsDetectionProfileParams", params),
            )

        msg = f"Unsupported acs detection profile: {profile}"
        raise ValueError(msg)
