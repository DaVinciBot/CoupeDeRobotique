"""Strategy that only deploys the banner before finishing."""

from __future__ import annotations

from typing import TYPE_CHECKING
from a_config_loader import CONFIG

from boombot_strategy.strategies.base_strategy import BaseStrategy
from boombot_strategy.sub_graphs import get_banner_deployment_subgraph
from boombot_strategy.tasks.navigation_tasks.go_to_color_reserved_zone import (
    GoToColorReservedZoneToFinishGame,
)
from log_manager import LogLogger
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

