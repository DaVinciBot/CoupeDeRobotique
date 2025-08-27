"""Parameter container for the rectangular ACS projection profile."""

from navigation.avoidance.acs_detection_profiles.base_acs_detection_profiles import (
    BaseAcsDetectionProfileParams,
)
from navigation.avoidance.acs_detection_profiles.struct import AcsDetectionProfile


class RectangularProjectionAcsDetectionProfileParams(BaseAcsDetectionProfileParams):
    """Parameters for the rectangular projection ACS detection profile."""

    def __init__(self, acs_distance: float, width_view: float) -> None:
        """Initializes the RectangularProjectionAcsDetectionProfileParams.

        Args:
            acs_distance (float): Distance to the obstacle.
            width_view (float): Width of the view.

        """
        self.width_view: float = width_view
        self.half_width_view: float = width_view / 2.0
        self.half_length_view: float = acs_distance / 2.0

        super().__init__(
            acs_detection_profile=AcsDetectionProfile.RECTANGULAR_PROJECTION,
            acs_distance=acs_distance,
        )
