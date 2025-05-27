# ====== Code Summary ======
# This module defines the BaseAvoidanceParams class, which encapsulates common configuration
# parameters shared across different obstacle avoidance strategies. It includes the selected
# avoidance strategy, the ACS (Automatic Collision System) trigger distance, and an optional
# timeout value for avoidance procedures.

# ====== Standard Library Imports ======
# (None)

# ====== Third-party Library Imports ======
# (None)

# ====== Internal Project Imports ======
from navigation.avoidance.structs import AvoidanceStrategy


class BaseAvoidanceParams:
    """
    Base class for defining common parameters used in avoidance strategies.

    This class serves as a container for configuration values such as the avoidance
    strategy type, the ACS detection distance, and a timeout duration.

    Attributes:
        avoidance_strategy (AvoidanceStrategy): Enum indicating the avoidance strategy.
    """

    def __init__(
        self,
        avoidance_strategy: AvoidanceStrategy,
    ):
        """
        Initialize the base avoidance parameters.

        Args:
            avoidance_strategy (AvoidanceStrategy): The selected avoidance strategy.

        """
        self.avoidance_strategy: AvoidanceStrategy = avoidance_strategy
