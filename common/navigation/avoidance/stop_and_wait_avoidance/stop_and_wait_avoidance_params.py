# ====== Code Summary ======
# This module defines the StopAndWaitAvoidanceParams class, which configures a stop-and-wait strategy
# for obstacle avoidance in a navigation system. It specifies the distance at which avoidance is triggered
# and the duration to wait before re-evaluating the path.


# ====== Internal Project Imports ======
from navigation.avoidance.structs import AvoidanceStrategy
from navigation.avoidance.base_avoidance import BaseAvoidanceParams


class StopAndWaitAvoidanceParams(BaseAvoidanceParams):
    """
    Configuration class for the 'STOP_AND_WAIT' obstacle avoidance strategy.

    This strategy stops the system when an obstacle is detected within a specified distance
    and waits for a defined timeout period before taking further action.

    Attributes:
        timeout (float): Duration (in seconds) to wait after stopping before reassessment.
    """

    def __init__(
        self,
        timeout: float,
    ):
        """
        Initializes StopAndWaitAvoidanceParams with specific avoidance distance and timeout in seconds.

        Args:
            timeout (float): Time to wait after stopping before checking again in seconds.
        """
        self.timeout: float = timeout * 1000.0
        super().__init__(AvoidanceStrategy.STOP_AND_WAIT)
