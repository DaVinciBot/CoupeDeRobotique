from __future__ import annotations

from typing import TYPE_CHECKING

from loggerplusplus import Logger

from strategy.core.sub_graphs import BaseSubGraph

if TYPE_CHECKING:
    from strategy.core.task_nodes.base_task_node import BaseTaskNode
    from strategy.core.transitions import BaseTransition


class SubGraphBuilder:
    """Builder for BaseSubGraph: assemble nodes and transitions, merge subgraphs,
    and produce a standalone subgraph ready for execution.

    """

    def __init__(self) -> None:
        self.logger = Logger(
            identifier="SubGraphBuilder",
            follow_logger_manager_rules=True,
        )
        self.nodes: dict[str, BaseTaskNode] = {}
        self._transitions: list[tuple[str, BaseTransition]] = []
        self.logger.info("Initialized SubGraphBuilder")

    def add_node(self, name: str, node: BaseTaskNode) -> SubGraphBuilder:
        """Register a task node.

        Args:
            name (str): Name for the node; must be unique.
            node (BaseTaskNode): Node instance to register.

        Returns:
            SubGraphBuilder: ``self`` to allow call chaining.

        Raises:
            KeyError: If ``name`` already exists in the builder.

        """
        if name in self.nodes:
            msg = f"Node name '{name}' already registered"
            self.logger.error(msg)
            raise KeyError(msg)
        self.nodes[name] = node
        self.logger.debug(f"Added node '{name}'")
        return self

    def connect(self, from_name: str, transition: BaseTransition) -> SubGraphBuilder:
        """Queue a transition from an existing node.

        Args:
            from_name (str): Name of the source node.
            transition (BaseTransition): Transition to append.

        Returns:
            SubGraphBuilder: ``self`` for chaining.

        Raises:
            KeyError: If ``from_name`` is not registered.

        """
        if from_name not in self.nodes:
            msg = f"Source node '{from_name}' not found for transition"
            self.logger.error(msg)
            raise KeyError(msg)
        self._transitions.append((from_name, transition))
        self.logger.debug(f"Queued transition on '{from_name}' -> {transition}")
        return self

    def add_subgraph(self, subgraph: BaseSubGraph, prefix: str = "") -> SubGraphBuilder:
        """Merge another subgraph into this builder.

        Args:
            subgraph (BaseSubGraph): The subgraph to merge.
            prefix (str, optional): Prefix for new node names. Defaults to "".

        Returns:
            SubGraphBuilder: ``self`` for chaining.

        """
        mapping: dict[BaseTaskNode, BaseTaskNode] = {}
        for old in subgraph.get_all_nodes():
            new_name = prefix + old.name
            new_node = type(old)(
                name=new_name,
                tasks=old.tasks,
                scoring_function=old.scoring_function,
            )
            self.add_node(new_name, new_node)
            mapping[old] = new_node
        for old in subgraph.get_all_nodes():
            from_new = mapping[old]
            for t in old.transitions:
                if t.target not in mapping:
                    continue
                new_transition = type(t)(mapping[t.target])
                from_new.add_transition(new_transition)
                self.logger.debug(
                    f"Recreated transition: '{from_new.name}' -> '{mapping[t.target].name}'",
                )
        return self

    def build(
        self,
        entry: str | BaseTaskNode,
        exits: str | BaseTaskNode | list[str | BaseTaskNode],
    ) -> BaseSubGraph:
        """Finalize construction and return a :class:``BaseSubGraph``.

        Args:
            entry (str | BaseTaskNode): Entry node or its name.
            exits (str | BaseTaskNode | list[str | BaseTaskNode]): One or more
                exit nodes or their names.

        Returns:
            BaseSubGraph: The assembled subgraph ready for execution.

        Raises:
            KeyError: If ``entry`` or any ``exits`` are not registered.

        """
        # Resolve entry
        entry_node = self._resolve(entry)
        # Resolve exits
        if isinstance(exits, list):
            exit_nodes = [self._resolve(e) for e in exits]
        else:
            exit_nodes = [self._resolve(exits)]
        # Apply transitions
        for from_name, transition in self._transitions:
            node = self.nodes[from_name]
            node.add_transition(transition)
            self.logger.debug(f"Connected '{from_name}' -> '{transition.target.name}'")
        # Validate
        missing = [n for n in exit_nodes if n.name not in self.nodes]
        if missing:
            msg = f"Exit nodes not registered: {[n.name for n in missing]}"
            self.logger.error(msg)
            raise KeyError(msg)
        self.logger.info(
            f"Building subgraph entry='{entry_node.name}' exits={[n.name for n in exit_nodes]}",
        )
        return BaseSubGraph(
            entry_node=entry_node,
            exit_nodes=exit_nodes,
            all_nodes=list(self.nodes.values()),
        )

    def _resolve(self, item: str | BaseTaskNode) -> BaseTaskNode:
        if isinstance(item, str):
            if item not in self.nodes:
                msg = f"Node '{item}' not found"
                self.logger.error(msg)
                raise KeyError(msg)
            return self.nodes[item]
        return item
