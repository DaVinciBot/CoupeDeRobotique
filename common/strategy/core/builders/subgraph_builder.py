# ====== Code Summary ======
# This code defines a builder class `SubGraphBuilder` used to construct and manipulate subgraphs composed of task nodes
# and transitions. It allows the addition of individual nodes, connection of transitions, and integration of existing
# subgraphs with optional name prefixing. The final subgraph can be constructed with specified entry and exit nodes.

# ====== Standard Library Imports ======
from typing import Dict, List, Union

# ====== Third-party Library Imports ======
# (None)

# ====== Internal Project Imports ======
from strategy.core.task_nodes import BaseTaskNode
from strategy.core.transitions import BaseTransition
from strategy.core.sub_graphs import BaseSubGraph


class SubGraphBuilder:
    """
    A builder class for creating subgraphs composed of task nodes and transitions.
    Allows for modular construction and merging of subgraphs.
    """

    def __init__(self):
        """
        Initialize the SubGraphBuilder with empty nodes and transition mappings.
        """
        self.nodes: Dict[str, BaseTaskNode] = {}
        self.transition_map: List[tuple[str, BaseTransition]] = []

    def _resolve_node(self, node: Union[str, BaseTaskNode]) -> BaseTaskNode:
        """
        Resolve a node from a string name or return the node directly.

        Args:
            node (Union[str, BaseTaskNode]): Node name or instance.

        Returns:
            BaseTaskNode: Resolved node instance.
        """
        return self.nodes[node] if isinstance(node, str) else node

    def add_node(self, name: str, node: BaseTaskNode) -> "SubGraphBuilder":
        """
        Add a node to the builder.

        Args:
            name (str): Name of the node.
            node (BaseTaskNode): The task node to add.

        Returns:
            SubGraphBuilder: The builder instance for chaining.
        """
        self.nodes[name] = node
        return self

    def connect(self, from_name: str, transition: BaseTransition) -> "SubGraphBuilder":
        """
        Queue a transition to be added between nodes.

        Args:
            from_name (str): Name of the source node.
            transition (BaseTransition): Transition to add from source.

        Returns:
            SubGraphBuilder: The builder instance for chaining.
        """
        self.transition_map.append((from_name, transition))
        return self

    def build(
        self,
        entry: Union[str, BaseTaskNode],
        exits: Union[str, BaseTaskNode, List[Union[str, BaseTaskNode]]],
    ) -> BaseSubGraph:
        """
        Build and return a BaseSubGraph with the specified entry and exit nodes.

        Args:
            entry (Union[str, BaseTaskNode]): Entry node (name or instance).
            exits (Union[str, BaseTaskNode, List[Union[str, BaseTaskNode]]]): Exit node(s) (names or instances).

        Returns:
            BaseSubGraph: The constructed subgraph.
        """
        # Apply queued transitions
        for from_name, transition in self.transition_map:
            self.nodes[from_name].add_transition(transition)

        # Resolve entry node
        entry_node = self._resolve_node(entry)

        # Resolve exit node(s)
        if isinstance(exits, list):
            exit_nodes = [self._resolve_node(e) for e in exits]
        else:
            exit_nodes = [self._resolve_node(exits)]

        return BaseSubGraph(
            entry_node=entry_node,
            exit_nodes=exit_nodes,
            all_nodes=list(self.nodes.values()),
        )

    def add_subgraph(
        self, subgraph: BaseSubGraph, prefix: str = ""
    ) -> "SubGraphBuilder":
        """
        Merge another subgraph into this builder, optionally prefixing node names to avoid conflicts.

        Returns:
            SubGraphBuilder: The builder instance for chaining.
        """
        node_mapping: Dict[BaseTaskNode, BaseTaskNode] = {}

        # Step 1: Clone nodes (shallow copy of tasks, new node instances)
        for old_node in subgraph.get_all_nodes():
            new_name = f"{prefix}{old_node.name}"

            new_node = type(old_node)(  # Same class (BaseTaskNode or dérivé)
                name=new_name,
                task=old_node.tasks,  # Optionnel : deepcopy(old_node.task) si side effects
                scoring_function=old_node.scoring_function,
            )
            self.nodes[new_name] = new_node
            node_mapping[old_node] = new_node

        # Step 2: Recreate transitions
        for from_old in subgraph.get_all_nodes():
            from_new = node_mapping[from_old]
            for t in from_old.transitions:
                to_old = t.target
                to_new = node_mapping[to_old]
                new_transition = type(t)(to_new)
                from_new.add_transition(new_transition)

        return self
