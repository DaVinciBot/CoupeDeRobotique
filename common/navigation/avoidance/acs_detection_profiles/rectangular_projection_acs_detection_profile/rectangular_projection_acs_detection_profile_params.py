from navigation.avoidance.acs_detection_profiles.struct import AcsDetectionProfile

from navigation.avoidance.acs_detection_profiles.base_acs_detection_profils import (
    BaseAcsDetectionProfileParams,
)


class RectangularProjectionAcsDetectionProfileParams(BaseAcsDetectionProfileParams):
    def __init__(self, acs_distance: float, width_view: float):
        self.width_view: float = width_view

        # Compute half dimensions for rectangle projection
        self.half_width_view: float = width_view / 2
        self.half_length_view: float = acs_distance / 2

        super().__init__(
            acs_detection_profile=AcsDetectionProfile.RECTANGULAR_PROJECTION,
            acs_distance=acs_distance,
        )
