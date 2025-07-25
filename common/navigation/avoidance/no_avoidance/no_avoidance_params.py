# ====== Code Summary ======
# This module defines the NoAvoidanceParams class, a configuration class used when no obstacle avoidance
# strategy is needed in a navigation system. It inherits from BaseAvoidanceParams and specifies a
# "NO_AVOIDANCE" strategy with zero avoidance distance.


from navigation.avoidance.base_avoidance import BaseAvoidanceParams
from navigation.avoidance.structs import AvoidanceStrategy


class NoAvoidanceParams(BaseAvoidanceParams):
    """Configuration class for navigation scenarios where no avoidance is required.

    This class sets the avoidance strategy to 'NO_AVOIDANCE' and disables any
    distance-based avoidance behavior by setting the avoidance distance to zero.

    """

    def __init__(self) -> None:
        """Initializes NoAvoidanceParams with 'NO_AVOIDANCE' strategy."""
        super().__init__(AvoidanceStrategy.NO_AVOIDANCE)
