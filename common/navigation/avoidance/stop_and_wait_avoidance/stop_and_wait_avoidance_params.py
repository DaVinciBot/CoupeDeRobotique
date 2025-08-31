"""Parameters for the stop-and-wait avoidance strategy."""

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
        """Initializes parameters with a timeout in seconds.

        Args:
            timeout (float):
                Time to wait after stopping before checking again in seconds.

        """
        super().__init__(AvoidanceStrategy.STOP_AND_WAIT, timeout * 1000.0)
