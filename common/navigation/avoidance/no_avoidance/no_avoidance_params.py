# ====== Code Summary ======
# This module defines the NoAvoidanceParams class, a configuration class used when no obstacle avoidance
# strategy is needed in a navigation system. It inherits from BaseAvoidanceParams and specifies a
# "NO_AVOIDANCE" strategy with zero avoidance distance.


# ====== Internal Project Imports ======
from navigation.avoidance.structs import AvoidanceStrategy
from navigation.avoidance.base_avoidance import BaseAvoidanceParams


class NoAvoidanceParams(BaseAvoidanceParams):
    """
    Configuration class for navigation scenarios where no avoidance is required.

    This class sets the avoidance strategy to 'NO_AVOIDANCE' and disables any
    distance-based avoidance behavior by setting the avoidance distance to zero.
    """

    def __init__(self):
        """
        Initializes NoAvoidanceParams with 'NO_AVOIDANCE' strategy and avoidance distance set to 0.
        """
        super().__init__(AvoidanceStrategy.NO_AVOIDANCE, acs_distance=0)
