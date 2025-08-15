"""Base classes for ACS detection profiles."""

from abc import ABC, abstractmethod

from loggerplusplus import Logger

from arena import AllyZone, EnemyZone
from navigation.avoidance.acs_detection_profiles import (
    BaseAcsDetectionProfileParams,
)


class BaseAcsDetectionProfile[PARAMSTYPE: BaseAcsDetectionProfileParams](ABC):
    """Base class for ACS detection profiles."""

    def __init__(self, params: PARAMSTYPE, logger: Logger | None = None) -> None:
        """Initializes the BaseAcsDetectionProfile.

        Args:
            params (PARAMSTYPE): Parameters for the ACS detection profile.
            logger (Logger | None, optional):
                Logger instance for debugging. Defaults to None.

        """
        self.params: PARAMSTYPE = params
        self.logger: Logger = logger or Logger(
            identifier=self.__class__.__name__,
            follow_logger_manager_rules=True,
        )

    @abstractmethod
    def is_acs_triggered(self, ally_zone: AllyZone, enemy_zone: EnemyZone) -> bool:
        """Determine if the anti-collision system should engage.

        Args:
            ally_zone (AllyZone): The robot's current zone.
            enemy_zone (EnemyZone): The detected enemy zone.

        Returns:
            bool: ``True`` if avoidance should be triggered, ``False`` otherwise.

        """
