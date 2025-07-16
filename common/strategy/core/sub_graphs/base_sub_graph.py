
from strategy.core.task_nodes.base_task_node import BaseTaskNode


class BaseSubGraph:
    def __init__(
        self,
        entry_node: BaseTaskNode,
        exit_nodes: BaseTaskNode | list[BaseTaskNode],
        all_nodes: list[BaseTaskNode],
    ):
        self.entry_node = entry_node
        self.exit_nodes = (
            [exit_nodes] if isinstance(exit_nodes, BaseTaskNode) else exit_nodes
        )
        self.all_nodes = all_nodes

    def get_entry(self) -> BaseTaskNode:
        return self.entry_node

    def get_exits(self) -> list[BaseTaskNode]:
        return self.exit_nodes

    def get_all_nodes(self) -> list[BaseTaskNode]:
        return self.all_nodes
