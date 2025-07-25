# ====== Code Summary ======
# This module defines the BackAndForwardAvoidanceParams class, which configures a back-and-forward strategy
# for obstacle avoidance in a navigation system. It specifies the distance at which avoidance is triggered
# and the duration to wait before re-evaluating the path.


from navigation.avoidance.base_avoidance import BaseAvoidanceParams
from navigation.avoidance.structs import AvoidanceStrategy
from navigation.trajectory_planner import SpeedProfiler


class BackAvoidanceParams(BaseAvoidanceParams):
    """Configuration for a backward avoidance strategy.

    This strategy stops the system when an obstacle is detected within a specified distance
    and waits for a defined timeout period before taking further action.

    """

    def __init__(
        self,
        timeout: float,
        backward_distance: float,
        backward_speed_profiler: SpeedProfiler,
    ) -> None:
        """Initialize parameters for backward avoidance.

        Args:
            timeout (float): Time to wait after stopping before checking again in seconds.
            backward_distance (float): Distance to reverse when avoidance is triggered.
            backward_speed_profiler (SpeedProfiler): Profiler for the backward motion.

        """
        self.backward_distance: float = backward_distance
        self.backward_speed_profiler: SpeedProfiler = backward_speed_profiler
        super().__init__(AvoidanceStrategy.BACK, timeout * 1000.0)
