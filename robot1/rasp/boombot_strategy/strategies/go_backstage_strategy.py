"""Strategy that only deploys the banner before finishing."""

from __future__ import annotations

from typing import TYPE_CHECKING
import math
from boombot_strategy.strategies.base_strategy import BaseStrategy
from boombot_strategy.tasks.navigation_tasks.maneuver import (
    RelativeBackward,
    RelativeForward,
    RelativeRotation,
)
from log_manager import LogLogger
from strategy.core import GraphRunner
from strategy.core.task_nodes import BaseTaskNode

if TYPE_CHECKING:
    from boombot_strategy.winter_game_context import WinterGameContext

POSITION_TOLERANCE_CM = 10.0
ANGLE_TOLERANCE_RAD = 0.15


class GoBackstageStrategy(BaseStrategy):
    """Deploy the banner then move directly to the backstage zone."""

    def __init__(self, ctx: WinterGameContext) -> None:
        """Initialize the strategy.

        Build the task flow using subgraphs and direct transitions.

        Args:
            ctx (WinterGameContext):
                Game context containing game-specific configurations and zones.
        """
        super().__init__(ctx)

        forward = BaseTaskNode(
            name="Move Forward",
            tasks=RelativeForward(
                distance=100.0,
                position_reached_tolerance_cm=POSITION_TOLERANCE_CM,
                angle_reached_tolerance_rad=ANGLE_TOLERANCE_RAD,
            ),
        )

        turn1 = BaseTaskNode(
            name="Turn 1",
            tasks=RelativeRotation(
                angle=math.pi / 2,
                position_reached_tolerance_cm=POSITION_TOLERANCE_CM,
                angle_reached_tolerance_rad=ANGLE_TOLERANCE_RAD,
            ),  # 90 degrees
        )

        forward2 = BaseTaskNode(
            name="Move Forward",
            tasks=RelativeForward(
                distance=10.0,
                position_reached_tolerance_cm=POSITION_TOLERANCE_CM,
                angle_reached_tolerance_rad=ANGLE_TOLERANCE_RAD,
            ),
        )

        turn2 = BaseTaskNode(
            name="Turn 2",
            tasks=RelativeRotation(
                angle=math.pi / 2,
                position_reached_tolerance_cm=POSITION_TOLERANCE_CM,
                angle_reached_tolerance_rad=ANGLE_TOLERANCE_RAD,
            ),  # 90 degrees
        )

        end = BaseTaskNode(
            name="End",
            tasks=RelativeForward(
                distance=100.0,
                position_reached_tolerance_cm=POSITION_TOLERANCE_CM,
                angle_reached_tolerance_rad=ANGLE_TOLERANCE_RAD,
            ),
        )

        # Connect the subgraphs in execution order
        self._auto_build_transitions(forward, turn1, forward2, turn2, end)

        # Create the graph runner starting from the first subgraph
        self.runner = GraphRunner(
            logger=LogLogger(
                identifier="GoBackstageStrategy",
                follow_logger_manager_rules=True,
            ),
            start=forward,
        )
