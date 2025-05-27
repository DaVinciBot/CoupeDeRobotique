from navigation.avoidance.acs_detection_profiles.base_acs_detection_profils.base_acs_detection_profils_params import (
    BaseAcsDetectionProfileParams,
)
from abc import ABC, abstractmethod
from typing import Generic, TypeVar


from arena import AllyZone, EnemyZone

ParamsType = TypeVar("ParamsType", bound=BaseAcsDetectionProfileParams)


class BaseAcsDetectionProfile(ABC, Generic[ParamsType]):
    def __init__(self, params: ParamsType):
        self.params: ParamsType = params

    @abstractmethod
    def is_acs_triggered(self, ally_zone: AllyZone, enemy_zone: EnemyZone) -> bool: ...
