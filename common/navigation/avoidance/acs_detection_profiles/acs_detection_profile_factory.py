"""Factory for ACS detection profiles.

This module selects a concrete profile implementation based on parameters.
"""

from typing import Any, cast

from navigation.avoidance.acs_detection_profiles import (
    AngularRestrictProjectionAcsDetectionProfile,
    AngularRestrictProjectionAcsDetectionProfileParams,
    BaseAcsDetectionProfile,
    BaseAcsDetectionProfileParams,
    NoAcsDetectionProfile,
    NoAcsDetectionProfileParams,
    NoProjectionAcsDetectionProfile,
    NoProjectionAcsDetectionProfileParams,
    RectangularProjectionAcsDetectionProfile,
    RectangularProjectionAcsDetectionProfileParams,
)
from navigation.avoidance.acs_detection_profiles.struct import AcsDetectionProfile


class AcsDetectionProfileFactory:
    """Factory class to instantiate the appropriate obstacle avoidance component based on strategy."""

    @staticmethod
    def instantiate(
        params: BaseAcsDetectionProfileParams,
    ) -> BaseAcsDetectionProfile[Any]:
        """Create an ACS detection profile instance based on strategy parameters.

        Args:
            params (BaseAcsDetectionProfileParams):
                Parameters describing the desired profile.

        Returns:
            BaseAcsDetectionProfile: The instantiated detection profile.

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

        message = f"Unsupported acs detection profile: {profile}"
        raise ValueError(message)
