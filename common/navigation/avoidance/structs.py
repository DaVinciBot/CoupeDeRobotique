# ====== Standard Library Imports ======
from enum import Enum, auto


class AvoidanceStrategy(Enum):
    NO_AVOIDANCE = auto()
    STOP_AND_WAIT = auto()
