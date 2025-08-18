from enum import Enum, auto


class AcsDetectionProfile(Enum):
    """Enumeration for ACS detection profiles.

    Attributes:
        NO: No detection.
        NO_PROJECTION: No projection.
        RECTANGULAR_PROJECTION: Rectangular projection.
        ANGULAR_RESTRICT_PROJECTION: Angular restrict projection.

    """

    NO = auto()
    """No detection."""
    NO_PROJECTION = auto()
    """No projection."""
    RECTANGULAR_PROJECTION = auto()
    """Rectangular projection."""
    ANGULAR_RESTRICT_PROJECTION = auto()
    """Angular restrict projection."""
