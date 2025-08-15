# ====== Code Summary ======
# This module defines the BaseAvoidanceParams class, which encapsulates common configuration
# parameters shared across different obstacle avoidance strategies. It includes the selected
# avoidance strategy, the ACS (Automatic Collision System) trigger distance, and an optional
# timeout value for avoidance procedures.


from navigation.avoidance.structs import AvoidanceStrategy


class BaseAvoidanceParams:
    """Base class for common parameters used in avoidance strategies.

    This class serves as a container for configuration values such as the avoidance
    strategy type, the ACS detection distance, and a timeout duration.

    """

    def __init__(
        self,
        avoidance_strategy: AvoidanceStrategy,
        timeout: float | None = None,
    ) -> None:
        """Initialize the base avoidance parameters.

        Args:
            avoidance_strategy (AvoidanceStrategy): The selected avoidance strategy.
            timeout (float | None, optional):
                Optional timeout for the avoidance procedure.

        """
        self.avoidance_strategy: AvoidanceStrategy = avoidance_strategy
        self.timeout: float | None = timeout
