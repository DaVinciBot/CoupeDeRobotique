"""Parameters for the no-op avoidance strategy."""

from navigation.avoidance.base_avoidance.base_avoidance_params import (
    BaseAvoidanceParams,
)
from navigation.avoidance.structs import AvoidanceStrategy


class NoAvoidanceParams(BaseAvoidanceParams):
    """Configuration class for navigation scenarios where no avoidance is required.

    This class sets the avoidance strategy to 'NO_AVOIDANCE' and disables any
    distance-based avoidance behavior by setting the avoidance distance to zero.

    """

    def __init__(self) -> None:
        """Initializes NoAvoidanceParams with 'NO_AVOIDANCE' strategy."""
        super().__init__(AvoidanceStrategy.NO_AVOIDANCE)
