"""Strategy that only deploys the banner before finishing."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

from boombot_strategy.strategies.base_strategy import BaseStrategy
from boombot_strategy.tasks.navigation_tasks.maneuver import (
    RelativeForward,
    RelativeRotation,
)
from log_manager import LogLogger
from strategy.core import GraphRunner
from strategy.core.task_nodes import BaseTaskNode

if TYPE_CHECKING:
    from boombot_strategy.winter_game_context import WinterGameContext

POSITION_TOLERANCE_CM = 0.9
ANGLE_TOLERANCE_RAD = 0.15
FINISH_AFTER_EXPECTED_END_DELAY_S = 15.0


class GoBackstageStrategy(BaseStrategy):
    """Deploy the banner then move directly to the backstage zone."""

    def __init__(self, ctx: WinterGameContext, rotation_sign: float = 1.0) -> None:
        """Initialize the strategy.

        Build the task flow using subgraphs and direct transitions.

        Args:
            ctx (WinterGameContext):
                Game context containing game-specific configurations and zones.
            rotation_sign (float):
                Direction multiplier for relative rotations.
        """
        super().__init__(ctx)

        forward = BaseTaskNode(
            name="Move Forward",
            tasks=RelativeForward(
                distance=85.0,
                position_reached_tolerance_cm=POSITION_TOLERANCE_CM,
                angle_reached_tolerance_rad=ANGLE_TOLERANCE_RAD,
                finish_after_expected_end_delay_s=FINISH_AFTER_EXPECTED_END_DELAY_S,
            ),
        )

        turn1 = BaseTaskNode(
            name="Turn 1",
            tasks=RelativeRotation(
                angle=rotation_sign * math.pi / 2,
                position_reached_tolerance_cm=POSITION_TOLERANCE_CM,
                angle_reached_tolerance_rad=ANGLE_TOLERANCE_RAD,
                finish_after_expected_end_delay_s=FINISH_AFTER_EXPECTED_END_DELAY_S,
            ),  # 90 degrees
        )

        forward2 = BaseTaskNode(
            name="Move Forward",
            tasks=RelativeForward(
                distance=10.5,
                position_reached_tolerance_cm=POSITION_TOLERANCE_CM,
                angle_reached_tolerance_rad=ANGLE_TOLERANCE_RAD,
                finish_after_expected_end_delay_s=FINISH_AFTER_EXPECTED_END_DELAY_S,
            ),
        )

        turn2 = BaseTaskNode(
            name="Turn 2",
            tasks=RelativeRotation(
                angle=rotation_sign * math.pi / 2,
                position_reached_tolerance_cm=POSITION_TOLERANCE_CM,
                angle_reached_tolerance_rad=0.05,
                finish_after_expected_end_delay_s=20.0,
            ),  # 90 degrees
        )

        end = BaseTaskNode(
            name="End",
            tasks=RelativeForward(
                distance=95.0,
                position_reached_tolerance_cm=POSITION_TOLERANCE_CM,
                angle_reached_tolerance_rad=ANGLE_TOLERANCE_RAD,
                finish_after_expected_end_delay_s=80.0,
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
