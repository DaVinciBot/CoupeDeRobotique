from config_loader import CONFIG
from abc import ABC, abstractmethod
from loggerplusplus import Logger

from strategy.core import (
    SubGraphBuilder,
    BaseTaskNode,
    DirectTransition,
    BaseSubGraph,
    GraphRunner,
)

from strategy.tools import (
    visualize_task_graph_from_node,
    visualize_task_graph,
    visualize_entire_subgraph,
)


class BaseStrategy(ABC):
    def __init__(self, color: str):
        self.zones = CONFIG.INFO_BY_TEAM[color]
        self.strategy = SubGraphBuilder()
        self.runner: GraphRunner | None = None
        self.logger = Logger(
            identifier=self.__class__.__name__, follow_logger_manager_rules=True
        )

    def visualize_strategy(self) -> None:
        visualize_task_graph_from_node(
            subgraph=self.strategy,
            title=self.__class__.__name__,
        )

    def get_graph_runner(self) -> GraphRunner:
        return self.runner
