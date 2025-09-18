"""Abstractions for groups of task nodes forming a sub-graph."""

from __future__ import annotations

from strategy.core.task_nodes.base_task_node import BaseTaskNode


class BaseSubGraph:
    """Collection of interconnected task nodes with defined entry and exits."""

    def __init__(
        self,
        entry_node: BaseTaskNode,
        exit_nodes: BaseTaskNode | list[BaseTaskNode],
        all_nodes: list[BaseTaskNode],
    ) -> None:
        """Initialize the sub-graph.

        Args:
            entry_node (BaseTaskNode): Node where execution begins.
            exit_nodes (BaseTaskNode | list[BaseTaskNode]):
                Single node or list of nodes marking exits.
            all_nodes (list[BaseTaskNode]): Every node composing the sub-graph.
        """
        self.entry_node = entry_node
        self.exit_nodes = (
            [exit_nodes] if isinstance(exit_nodes, BaseTaskNode) else exit_nodes
        )
        self.all_nodes = all_nodes

    def get_entry(self) -> BaseTaskNode:
        """Get the entry node of the sub-graph.

        Returns:
            BaseTaskNode: The entry node.
        """
        return self.entry_node

    def get_exits(self) -> list[BaseTaskNode]:
        """Get the exit nodes of the sub-graph.

        Returns:
            list[BaseTaskNode]: The exit nodes.
        """
        return self.exit_nodes

    def get_all_nodes(self) -> list[BaseTaskNode]:
        """Get all nodes in the sub-graph.

        Returns:
            list[BaseTaskNode]: All nodes in the sub-graph.
        """
        return self.all_nodes
