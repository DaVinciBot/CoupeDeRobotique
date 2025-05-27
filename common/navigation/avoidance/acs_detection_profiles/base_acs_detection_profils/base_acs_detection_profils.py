from navigation.avoidance.acs_detection_profiles.struct import AcsDetectionProfile
from abc import ABC, abstractmethod

from arena import AllyZone, EnemyZone


class BaseAcsDetectionProfile(ABC):
    def __init__(self, acs_distance: float):
        self.acs_distance: float = acs_distance

    @abstractmethod
    def is_acs_triggered(self, ally_zone: AllyZone, enemy_zone: EnemyZone) -> bool: ...
