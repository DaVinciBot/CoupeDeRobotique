from typing import cast

from navigation.avoidance.acs_detection_profiles.angular_restrict_projection_acs_detection_profile import (
    AngularRestrictProjectionAcsDetectionProfile,
    AngularRestrictProjectionAcsDetectionProfileParams,
)
from navigation.avoidance.acs_detection_profiles.base_acs_detection_profils import (
    BaseAcsDetectionProfile,
    BaseAcsDetectionProfileParams,
)
from navigation.avoidance.acs_detection_profiles.no_acs_detection_profile import (
    NoAcsDetectionProfile,
    NoAcsDetectionProfileParams,
)
from navigation.avoidance.acs_detection_profiles.no_projection_acs_detection_profile import (
    NoProjectionAcsDetectionProfile,
    NoProjectionAcsDetectionProfileParams,
)
from navigation.avoidance.acs_detection_profiles.rectangular_projection_acs_detection_profile import (
    RectangularProjectionAcsDetectionProfile,
    RectangularProjectionAcsDetectionProfileParams,
)
from navigation.avoidance.acs_detection_profiles.struct import AcsDetectionProfile


class AcsDetectionProfileFactory:
    """Factory class to instantiate the appropriate obstacle avoidance component based on strategy."""

    @staticmethod
    def instantiate(params: BaseAcsDetectionProfileParams) -> BaseAcsDetectionProfile:
        """Create an ACS detection profile instance based on strategy parameters.

        Args:
            params (BaseAcsDetectionProfileParams): Parameters describing the desired profile.

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

        raise ValueError(f"Unsupported acs detection profile: {profile}")
