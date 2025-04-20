from navigation.avoidance.structs import AvoidanceStrategy

from navigation.avoidance.base_avoidance import BaseAvoidanceParams


class StopAndWaitAvoidanceParams(BaseAvoidanceParams):
    def __init__(self, acs_distance: float, timeout: float):
        super().__init__(AvoidanceStrategy.STOP_AND_WAIT, acs_distance, timeout)
