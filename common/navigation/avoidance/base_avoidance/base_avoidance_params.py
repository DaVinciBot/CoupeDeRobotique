from navigation.avoidance.structs import AvoidanceStrategy


class BaseAvoidanceParams:

    def __init__(self, avoidance_strategy: AvoidanceStrategy, acs_distance: float):
        self.avoidance_strategy: AvoidanceStrategy = avoidance_strategy
        self.acs_distance: float = acs_distance
