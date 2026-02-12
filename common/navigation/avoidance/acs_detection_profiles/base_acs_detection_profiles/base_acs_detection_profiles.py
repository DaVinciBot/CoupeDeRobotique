"""Base classes for ACS detection profiles."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from log_manager import LogLogger
from navigation.avoidance.acs_detection_profiles.base_acs_detection_profiles.base_acs_detection_profiles_params import (  # noqa: E501
    BaseAcsDetectionProfileParams,
)

if TYPE_CHECKING:
    from loggerplusplus import Logger

    from arena.base_arena.arena_zones import AllyZone, EnemyZone


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
        self._logger: Logger = logger or LogLogger(
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
