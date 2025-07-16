
from enum import Enum, auto


class AcsDetectionProfile(Enum):
    NO = auto()
    NO_PROJECTION = auto()
    RECTANGULAR_PROJECTION = auto()
    ANGULAR_RESTRICT_PROJECTION = auto()
