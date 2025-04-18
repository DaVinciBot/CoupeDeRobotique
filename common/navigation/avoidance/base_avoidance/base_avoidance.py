# ====== Imports ======
# Standard library imports
from abc import ABC, abstractmethod
from typing import Generic, TypeVar
import functools
# Third-party imports
from loggerplusplus import Logger

# Local imports
from arena import AllyZone, EnemyZone
import copy
# Internal project imports
from navigation.avoidance.base_avoidance.base_avoidance_params import BaseAvoidanceParams
from navigation.avoidance.base_avoidance.states import AvoidanceState
from navigation.trajectory_planner import TrajectoryPlanCommand

# ====== Type Hint ======
ParamsType = TypeVar("ParamsType", bound=BaseAvoidanceParams)


# ====== Base Avoidance Class ======
class BaseAvoidance(ABC, Generic[ParamsType]):
    def __init__(self, params: ParamsType, logger: Logger | None = None) -> None:
        self.logger: Logger = logger or Logger(identifier=self.__class__.__name__, follow_logger_manager_rules=True)

        self.params: ParamsType = params

        self.state: AvoidanceState = AvoidanceState.IDLE

        self._original_task: 'NavigatorTask' = None

    def _acs(self, ally_zone: AllyZone, enemy_zone: EnemyZone) -> bool:
        return ally_zone.point.distance(enemy_zone.point) <= self.params.acs_distance


    def _store_original_task(self, current_navigator_task: 'NavigatorTask') -> None:
        if self._original_task is None and self.state == AvoidanceState.IDLE:
            # Store the original task
            self._original_task: 'NavigatorTask' = copy.deepcopy(current_navigator_task)

    @staticmethod
    def _ensure_original_task_storage(method: callable) -> callable:
        @functools.wraps(method)
        def wrapper(self, current_navigator_task: 'NavigatorTask', *args, **kwargs):
            self._store_original_task(current_navigator_task)
            # Execute the method
            return method(self, current_navigator_task, *args, **kwargs)

        return wrapper

    @abstractmethod
    def handle(self, current_navigator_task: 'NavigatorTask', ally_zone: AllyZone,
               enemy_zone: EnemyZone) -> 'NavigatorTask':
        ...
