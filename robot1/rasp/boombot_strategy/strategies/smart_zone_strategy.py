"""Strategy that only deploys the banner before finishing."""

from __future__ import annotations

from math import pi

from typing import TYPE_CHECKING
from a_config_loader import CONFIG

from boombot_strategy.strategies.base_strategy import BaseStrategy
from boombot_strategy.sub_graphs import (
    get_pickup_jenga_subgraph,
    get_deposit_jenga_color_zone_subgraph,
    get_deposit_jenga_deposit_zone_subgraph,
    get_cursor_alignment_backward_subgraph,
    get_cursor_alignment_forward_subgraph,
)

from geometry import OrientedPoint
from log_manager import LogLogger
from boombot_strategy.tasks.navigation_tasks.go_to_color_reserved_zone import (
    GoToColorReservedZoneToFinishGame,
)
from strategy.core import GraphRunner
from strategy.core.task_nodes import BaseTaskNode

if TYPE_CHECKING:
    from boombot_strategy.winter_game_context import WinterGameContext


class SmartZoneStrategy(BaseStrategy):
    def __init__(self, ctx: WinterGameContext) -> None:

        super().__init__(ctx)
        self.pickup_zones = CONFIG.PICKUP_ZONES
        self.pickup_zones_list = CONFIG.PICKUP_ZONES_LIST
        self.deposit_zones = CONFIG.DEPOSIT_ZONES
        self.deposit_zones_list = CONFIG.DEPOSIT_ZONES_LIST
        self.color_zone = CONFIG.TEAM_SPECIFIC_ZONES[ctx.arena.team_color.value]

        cursor_graph = None
        goal = OrientedPoint(0, 0, 0)

        if ctx.arena.team_color.name.lower() == "yellow":
            goal = OrientedPoint(10, 10, 0)
            cursor_graph = get_cursor_alignment_backward_subgraph(goal, ctx)
        elif ctx.arena.team_color.name.lower() == "blue":
            goal = OrientedPoint(290, 10, pi)
            cursor_graph = get_cursor_alignment_forward_subgraph(goal, ctx)

        pickup_graph_1 = get_pickup_jenga_subgraph(self.pickup_zones_list[0], ctx)
        pickup_graph_2 = get_pickup_jenga_subgraph(self.pickup_zones_list[1], ctx)
        pickup_graph_3 = get_pickup_jenga_subgraph(self.pickup_zones_list[2], ctx)
        pickup_graph_4 = get_pickup_jenga_subgraph(self.pickup_zones_list[3], ctx)
        pickup_graph_5 = get_pickup_jenga_subgraph(self.pickup_zones_list[4], ctx)
        pickup_graph_6 = get_pickup_jenga_subgraph(self.pickup_zones_list[5], ctx)
        pickup_graph_7 = get_pickup_jenga_subgraph(self.pickup_zones_list[6], ctx)
        pickup_graph_8 = get_pickup_jenga_subgraph(self.pickup_zones_list[7], ctx)

        deposit_graph_1 = get_deposit_jenga_deposit_zone_subgraph(self.deposit_zones_list[0], ctx)
        deposit_graph_2 = get_deposit_jenga_deposit_zone_subgraph(self.deposit_zones_list[1], ctx)
        deposit_graph_3 = get_deposit_jenga_deposit_zone_subgraph(self.deposit_zones_list[2], ctx)
        deposit_graph_4 = get_deposit_jenga_deposit_zone_subgraph(self.deposit_zones_list[3], ctx)
        deposit_graph_5 = get_deposit_jenga_deposit_zone_subgraph(self.deposit_zones_list[4], ctx)
        deposit_graph_6 = get_deposit_jenga_deposit_zone_subgraph(self.deposit_zones_list[5], ctx)
        deposit_graph_7 = get_deposit_jenga_deposit_zone_subgraph(self.deposit_zones_list[6], ctx)
        deposit_graph_8 = get_deposit_jenga_deposit_zone_subgraph(self.deposit_zones_list[7], ctx)
        deposit_graph_9 = get_deposit_jenga_deposit_zone_subgraph(self.deposit_zones_list[8], ctx)
        deposit_graph_10 = get_deposit_jenga_deposit_zone_subgraph(self.deposit_zones_list[9], ctx)

        go_to_backstage = BaseTaskNode(
            name="[End] Go to backstage",
            tasks=GoToColorReservedZoneToFinishGame(self.zones["backstage_zone"], ctx),
        )

        self._auto_build_transitions(
            cursor_graph,
            pickup_graph_1,
            deposit_graph_1,
            pickup_graph_2,
            deposit_graph_2,
            pickup_graph_3,
            deposit_graph_3,
            pickup_graph_4,
            deposit_graph_4,
            pickup_graph_5,
            deposit_graph_5,
            pickup_graph_6,
            deposit_graph_6,
            pickup_graph_7,
            deposit_graph_7,
            pickup_graph_8,
            deposit_graph_8,
            deposit_graph_9,
            deposit_graph_10,
            go_to_backstage,
        )

        self.runner = GraphRunner(
            logger=LogLogger(
                identifier="SmartZoneStrategyRunner",
                follow_logger_manager_rules=True,
            ),
            start=cursor_graph.get_entry(),
        )