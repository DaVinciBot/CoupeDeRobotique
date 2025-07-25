# ====== Code Summary ======
# This module defines the StopAndWaitAvoidanceParams class, which configures a stop-and-wait strategy
# for obstacle avoidance in a navigation system. It specifies the distance at which avoidance is triggered
# and the duration to wait before re-evaluating the path.


from navigation.avoidance.base_avoidance import BaseAvoidanceParams
from navigation.avoidance.structs import AvoidanceStrategy


class StopAndWaitAvoidanceParams(BaseAvoidanceParams):
    """Parameters for the ``STOP_AND_WAIT`` avoidance strategy.

    This strategy stops the system when an obstacle is detected and waits for a
    defined timeout period before reassessing the situation.
    """

    def __init__(
        self,
        timeout: float,
    ) -> None:
        """Initializes StopAndWaitAvoidanceParams with specific avoidance distance and timeout in seconds.

        Args:
            timeout (float): Time to wait after stopping before checking again in seconds.
        """
        super().__init__(AvoidanceStrategy.STOP_AND_WAIT, timeout * 1000.0)
