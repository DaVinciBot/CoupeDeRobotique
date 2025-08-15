"""Parameter base class for ACS detection profiles.

Stores the profile type and detection distance.
"""

from navigation.avoidance.acs_detection_profiles.struct import AcsDetectionProfile


class BaseAcsDetectionProfileParams:
    """Base class for ACS detection profile parameters."""

    def __init__(
        self,
        acs_detection_profile: AcsDetectionProfile,
        acs_distance: float,
    ) -> None:
        """Initialize the parameters for an ACS detection profile.

        Args:
            acs_detection_profile (AcsDetectionProfile):
                The type of ACS detection profile.
            acs_distance (float): The distance to the obstacle.

        """
        self.acs_detection_profile: AcsDetectionProfile = acs_detection_profile
        self.acs_distance: float = acs_distance

    @classmethod
    def from_config(
        cls,
        acs_detection_profile: str,
        acs_distance: float,
    ) -> "BaseAcsDetectionProfileParams":
        """Create parameters from textual configuration.

        Args:
            acs_detection_profile (str): The name of the ACS detection profile.
            acs_distance (float): The distance to the obstacle.

        Returns:
            BaseAcsDetectionProfileParams: The created instance.

        """
        return cls(
            acs_detection_profile=AcsDetectionProfile[acs_detection_profile.upper()],
            acs_distance=acs_distance,
        )
