

from navigation.avoidance.base_avoidance import BaseAvoidance, BaseAvoidanceParams


from navigation.avoidance.acs_detection_profiles.struct import AcsDetectionProfile
from abc import ABC, abstractmethod

from arena import AllyZone, EnemyZone
class NoProjectionAcsDetectionProfile(BaseAvoidance):
    def __init__(self, acs_distance: float):
        super().__init__(BaseAvoidanceParams(acs_distance=acs_distance))
        self.acs_distance: float = acs_distance

    @abstractmethod
    def is_acs_triggered(self, ally_zone: AllyZone, enemy_zone: EnemyZone) -> bool:
        pass