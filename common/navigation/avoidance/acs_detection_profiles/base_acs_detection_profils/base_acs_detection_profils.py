from navigation.avoidance.acs_detection_profiles.struct import AcsDetectionProfile
from abc import ABC, abstractmethod

from arena import AllyZone, EnemyZone
class BaseAcsDetectionProfile(ABC):

    def __init__(
            self,
            acs_detection_profile: AcsDetectionProfile
    ):
        self.acs_detection_profile: AcsDetectionProfile = acs_detection_profile

    @abstractmethod
    def is_acs_triggered(
            self,
            ally_zone: AllyZone,
            enemy_zone: EnemyZone
    ) -> bool:
        ...


