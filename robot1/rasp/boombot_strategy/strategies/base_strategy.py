"""Base classes for constructing robot strategies."""

from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING

from a_config_loader import CONFIG
from log_manager import LogLogger
from strategy.core.builders import SubGraphBuilder
from strategy.core.sub_graphs import BaseSubGraph
from strategy.core.transitions import DirectTransition
from strategy.tools import visualize_task_graph

if TYPE_CHECKING:
    from strategy.core import BaseGameContext, GraphRunner
    from strategy.core.task_nodes import BaseTaskNode


class BaseStrategy(ABC):
    """Base class for all strategies.

    This class provides a base implementation for all strategies.
    """

    def __init__(self, ctx: BaseGameContext) -> None:
        """Initialize the BaseStrategy.

        Args:
            ctx (BaseGameContext): The game context.
        """
        self.zones = CONFIG.INFO_BY_TEAM[ctx.arena.team_color.value]
        self.strategy = SubGraphBuilder()
        self.runner: GraphRunner
        self._logger = LogLogger(
            identifier=self.__class__.__name__,
            follow_logger_manager_rules=True,
        )

    def visualize_strategy(self) -> None:
        """Visualize the strategy.

        This method visualizes the strategy using the visualize_task_graph function.

        Raises:
            RuntimeError: If the strategy graph has not been built yet.
        """
        if not self.runner:
            msg = "Strategy graph has not been built yet."
            self._logger.error(f"[STRAT] Cannot visualize - no active graph. {msg}")
            raise RuntimeError(msg)
        visualize_task_graph(start_node=self.runner.active[0])

    def get_graph_runner(self) -> GraphRunner:
        """Get the graph runner.

        Returns:
            GraphRunner: The graph runner.

        Raises:
            RuntimeError: If the strategy graph has not been built yet.
        """
        if not self.runner:
            msg = "Strategy graph has not been built yet."
            self._logger.error(
                f"[STRAT] Cannot retrieve runner - no active graph. {msg}",
            )
            raise RuntimeError(msg)
        return self.runner

    def _auto_build_transitions(
        self,
        *elements: BaseTaskNode | BaseSubGraph,
    ) -> bool:
        """Build a subgraph using the provided TaskNodes or SubGraphs.

        Accepts any number of arguments of type BaseTaskNode or BaseSubGraph.

        Args:
            *elements (BaseTaskNode | BaseSubGraph):
                A variable number of nodes or subgraphs.

        Returns:
            bool:
                ``True`` if the transitions were built successfully,
                ``False`` otherwise.
        """
        if not elements:
            self._logger.error("[STRAT] No elements provided for building")
            return False

        # Resolve entry and exit points for each element
        entry_points = [self._resolve_for_entry(el) for el in elements]
        exit_points = [self._resolve_for_exits(el) for el in elements]
        for i in range(len(entry_points) - 1):
            # Create a direct transition from the exit of the current element
            # to the entry of the next
            self._logger.debug(
                f"[STRAT] Creating transition: "
                f"{exit_points[i].name} -> {entry_points[i + 1].name}",
            )
            exit_points[i].add_transition(DirectTransition(entry_points[i + 1]))
        return True

    @staticmethod
    def _resolve_for_entry(element: BaseTaskNode | BaseSubGraph) -> BaseTaskNode:
        """Resolve a TaskNode or SubGraph to its entry point.

        Args:
            element (BaseTaskNode | BaseSubGraph): The element to resolve.

        Returns:
            BaseTaskNode: The entry point of the resolved element.
        """
        if isinstance(element, BaseSubGraph):
            return element.get_entry()
        return element

    @staticmethod
    def _resolve_for_exits(element: BaseTaskNode | BaseSubGraph) -> BaseTaskNode:
        """Resolve a TaskNode or SubGraph to its exit points.

        Args:
            element (BaseTaskNode | BaseSubGraph): The element to resolve.

        Returns:
            BaseTaskNode: The exit point of the resolved element.
        """
        if isinstance(element, BaseSubGraph):
            return element.get_exits()[0]
        return element
