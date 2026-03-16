"""Non-linear jenga pick and deposit strategy."""

from __future__ import annotations

from math import pi
from typing import TYPE_CHECKING

from a_config_loader import CONFIG
from boombot_strategy.strategies.base_strategy import BaseStrategy
from boombot_strategy.tasks.actuator_tasks import (
    BlockJenga,
    DeployCursor,
    PrepareRotation,
    RotateJenga,
    SafeRetractAll,
)
from boombot_strategy.tasks.navigation_tasks import (
    GoToDepositZone,
    GoToStuffZoneToPickUp,
    RelativeBackward,
    RelativeForward,
)
from boombot_strategy.tasks.navigation_tasks.go_to_color_reserved_zone import (
    GoToColorReservedZoneToFinishGame,
)
from boombot_strategy.tasks.navigation_tasks.go_to_cursor_start import GoToCursorStart
from geometry import OrientedPoint
from log_manager import LogLogger
from strategy.core import GraphRunner
from strategy.core.task_nodes import BaseTaskNode
from strategy.core.task_nodes.scoring_functions import ConstantScoringFunction
from strategy.core.transitions import DirectTransition

if TYPE_CHECKING:
    from boombot_strategy.winter_game_context import WinterGameContext


class SmartZoneStrategy(BaseStrategy):
    def __init__(self, ctx: WinterGameContext) -> None:
        super().__init__(ctx)
        self.pickup_zones_list = CONFIG.PICKUP_ZONES_LIST
        self.deposit_zones_list = CONFIG.DEPOSIT_ZONES_LIST

        if ctx.arena.team_color.name.lower() == "yellow":
            goal = OrientedPoint(10, 10, 0)
            cursor_tasks = [
                GoToCursorStart(goal, ctx),
                DeployCursor(),
                RelativeBackward(20),
            ]
        else:
            goal = OrientedPoint(290, 10, pi)
            cursor_tasks = [
                GoToCursorStart(goal, ctx),
                DeployCursor(),
                RelativeForward(20),
            ]

        cursor_node = BaseTaskNode(
            name="[Cursor] Align",
            tasks=cursor_tasks,
            repeatable=False,
            max_visits=1,
        )

        pickup_nodes: list[BaseTaskNode] = [
            BaseTaskNode(
                name=f"[Pickup Jenga] Zone {zone_id}",
                tasks=[
                    GoToStuffZoneToPickUp(zone_id, ctx),
                    RelativeForward(5),
                    BlockJenga(),
                ],
                repeatable=True,
                max_visits=None,
            )
            for zone_id in self.pickup_zones_list
        ]

        deposit_nodes: list[BaseTaskNode] = [
            BaseTaskNode(
                name=f"[Deposit Jenga] Zone {zone_id}",
                tasks=[
                    GoToDepositZone(zone_id, ctx),
                    PrepareRotation(),
                    RotateJenga(),
                    SafeRetractAll(),
                ],
                repeatable=True,
                max_visits=None,
            )
            for zone_id in self.deposit_zones_list
        ]

        go_to_backstage = BaseTaskNode(
            name="[End] Go to backstage",
            tasks=GoToColorReservedZoneToFinishGame(self.zones["backstage_zone"], ctx),
            scoring_function=ConstantScoringFunction(
                score=-1e9,
            ),  # TODO: pas hardcoder le score
            repeatable=False,
            max_visits=1,
        )

        for pickup_node in pickup_nodes:
            for deposit_node in deposit_nodes:
                pickup_node.add_transition(
                    DirectTransition(deposit_node)
                )  # TODO: add conditions to avoid going to deposit if il est déjà plein
            pickup_node.add_transition(DirectTransition(go_to_backstage))

        for deposit_node in deposit_nodes:
            for pickup_node in pickup_nodes:
                deposit_node.add_transition(DirectTransition(pickup_node))
            deposit_node.add_transition(DirectTransition(go_to_backstage))

        for pickup_node in pickup_nodes:
            cursor_node.add_transition(DirectTransition(pickup_node))
        cursor_node.add_transition(DirectTransition(go_to_backstage))

        self.runner = GraphRunner(
            logger=LogLogger(
                identifier="SmartZoneStrategyRunner",
                follow_logger_manager_rules=True,
            ),
            start=cursor_node,
        )
