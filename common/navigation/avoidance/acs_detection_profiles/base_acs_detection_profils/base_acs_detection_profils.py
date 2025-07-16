from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from loggerplusplus import Logger

from arena import AllyZone, EnemyZone
from navigation.avoidance.acs_detection_profiles.base_acs_detection_profils.base_acs_detection_profils_params import (
    BaseAcsDetectionProfileParams,
)

ParamsType = TypeVar("ParamsType", bound=BaseAcsDetectionProfileParams)


class BaseAcsDetectionProfile(ABC, Generic[ParamsType]):
    def __init__(self, params: ParamsType, logger: Logger | None = None) -> None:
        self.params: ParamsType = params
        self.logger: Logger = logger or Logger(
            identifier=self.__class__.__name__,
            follow_logger_manager_rules=True,
        )

    @abstractmethod
    def is_acs_triggered(self, ally_zone: AllyZone, enemy_zone: EnemyZone) -> bool: ...
