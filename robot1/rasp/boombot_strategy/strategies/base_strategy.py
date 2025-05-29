from config_loader import CONFIG
from abc import ABC, abstractmethod
from loggerplusplus import Logger

from strategy.core import (
    SubGraphBuilder,
    BaseTaskNode,
    DirectTransition,
    BaseSubGraph,
    GraphRunner,
    BaseGameContext,
)

from strategy.tools import (
    visualize_task_graph,
)


class BaseStrategy(ABC):
    def __init__(self, ctx: BaseGameContext):
        self.zones = CONFIG.INFO_BY_TEAM[ctx.arena.team_color.value]
        self.strategy = SubGraphBuilder()
        self.runner: GraphRunner | None = None
        self.logger = Logger(
            identifier=self.__class__.__name__, follow_logger_manager_rules=True
        )

    def visualize_strategy(self) -> None:
        visualize_task_graph(start_node=self.runner.active[0])

    def get_graph_runner(self) -> GraphRunner:
        return self.runner
