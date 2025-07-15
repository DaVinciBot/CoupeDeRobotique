from config_loader import CONFIG
from abc import ABC, abstractmethod
from loggerplusplus import Logger
from typing import Union

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

    def _auto_build_transitions(
        self, *elements: Union[BaseTaskNode, BaseSubGraph]
    ) -> bool:
        """
        Build a subgraph using the provided TaskNodes or SubGraphs.

        Accepts any number of arguments of type BaseTaskNode or BaseSubGraph.

        Args:
            *elements (Union[BaseTaskNode, BaseSubGraph]): A variable number of nodes or subgraphs.

        Returns:
            bool: The result of the build process.
        """
        if not elements:
            self.logger.error("No elements provided for building the strategy.")
            return False
        if not all(isinstance(el, (BaseTaskNode, BaseSubGraph)) for el in elements):
            self.logger.error(
                "All elements must be of type BaseTaskNode or BaseSubGraph."
            )
            return False

        # Resolve entry and exit points for each element
        entry_points = [self._resolve_for_entry(el) for el in elements]
        exit_points = [self._resolve_for_exits(el) for el in elements]
        for i in range(len(entry_points) - 1):
            # Create a direct transition from the exit of the current element to the entry of the next
            self.logger.debug(
                f"Creating transition from {exit_points[i].name} to {entry_points[i + 1].name}"
            )
            exit_points[i].add_transition(DirectTransition(entry_points[i + 1]))
        return True

    def _resolve_for_entry(
        self, element: Union[BaseTaskNode, BaseSubGraph]
    ) -> BaseTaskNode:
        """
        Resolve a TaskNode or SubGraph to its entry point.

        Args:
            element (Union[BaseTaskNode, BaseSubGraph]): The element to resolve.

        Returns:
            BaseTaskNode: The entry point of the resolved element.
        """
        if isinstance(element, BaseSubGraph):
            return element.get_entry()
        return element

    def _resolve_for_exits(
        self, element: Union[BaseTaskNode, BaseSubGraph]
    ) -> BaseTaskNode:
        """
        Resolve a TaskNode or SubGraph to its exit points.

        Args:
            element (Union[BaseTaskNode, BaseSubGraph]): The element to resolve.

        Returns:
            BaseTaskNode: The exit point of the resolved element.
        """
        if isinstance(element, BaseSubGraph):
            return element.get_exits()[0]
        return element
