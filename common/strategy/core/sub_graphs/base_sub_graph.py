from typing import List, Union
from strategy.core.task_nodes.base_task_node import BaseTaskNode


class BaseSubGraph:
    def __init__(
        self,
        entry_node: BaseTaskNode,
        exit_nodes: Union[BaseTaskNode, List[BaseTaskNode]],
        all_nodes: List[BaseTaskNode],
    ):
        self.entry_node = entry_node
        self.exit_nodes = (
            [exit_nodes] if isinstance(exit_nodes, BaseTaskNode) else exit_nodes
        )
        self.all_nodes = all_nodes

    def get_entry(self) -> BaseTaskNode:
        return self.entry_node

    def get_exits(self) -> List[BaseTaskNode]:
        return self.exit_nodes

    def get_all_nodes(self) -> List[BaseTaskNode]:
        return self.all_nodes
