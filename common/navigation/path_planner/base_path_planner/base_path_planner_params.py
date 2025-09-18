"""Parameter containers for path planners."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from geometry import OrientedPoint
    from navigation.path_planner.structs import PathPlanningStrategy


class BasePathPlannerParams:
    """Base class for path planner parameter configurations."""

    def __init__(self, path_finding_strategy: PathPlanningStrategy) -> None:
        """Initialize the base path planner parameters.

        Args:
            path_finding_strategy (PathPlanningStrategy): Strategy for path finding.
        """
        self.path_finding_strategy: PathPlanningStrategy = path_finding_strategy


@dataclass
class BasePathPlannerPlanPathParams:
    """Parameters passed to :meth:`BasePathPlanner.plan_path`.

    Attributes:
        start (OrientedPoint): The starting point of the path.
    """

    start: OrientedPoint
