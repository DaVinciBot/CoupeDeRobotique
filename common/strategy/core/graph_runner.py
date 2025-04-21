# ====== Code Summary ======
# This module defines the `GraphRunner` class, which controls the execution flow of a graph of task nodes.
# It supports both parallel and sequential execution paths. Each node performs its task and may transition
# to one or more subsequent nodes based on the game context and transition conditions.

# ====== Standard Library Imports ======
from typing import List, Dict, Optional


# ====== Internal Project Imports ======
from strategy.core.task_nodes.base_task_node import BaseTaskNode
from strategy.core.transitions.base_transition import BaseTransition
from strategy.core.base_game_context import BaseGameContext


class GraphRunner:
    """
    Executes a task graph, managing task node transitions and execution flow.

    Attributes:
        parallel (bool): Determines whether transitions are handled in parallel or sequentially.
        active (List[BaseTaskNode]): List of currently active task nodes.
        prev (Dict[BaseTaskNode, Optional[BaseTaskNode]]): Mapping of each node to its predecessor.
    """

    def __init__(self, start: BaseTaskNode, parallel: bool = False) -> None:
        """
        Initializes the GraphRunner with a starting task node.

        Args:
            start (BaseTaskNode): The entry point node in the task graph.
            parallel (bool, optional): If True, all valid transitions are followed in parallel. Defaults to False.
        """
        self.parallel = parallel
        self.active: List[BaseTaskNode] = [start]
        self.prev: Dict[BaseTaskNode, Optional[BaseTaskNode]] = {start: None}

    def handle(self, ctx: BaseGameContext) -> None:
        """
        Executes the current active nodes and determines the next active nodes based on transition rules.

        Args:
            ctx (BaseGameContext): The current context used to evaluate task completion and transitions.
        """
        next_active: List[BaseTaskNode] = []

        for node in self.active:
            prev_node = self.prev.get(node)

            # 1. Execute the task
            done = node.handle(ctx)

            if not done:
                # If the task is not complete, keep it active
                next_active.append(node)
                continue

            # 2. Retrieve valid transitions
            valid: List[BaseTransition] = [
                t
                for t in node.transitions
                if t.can_transit(from_node=prev_node, ctx=ctx)
            ]

            if not valid:
                # End of branch if no valid transitions are found
                continue

            if self.parallel:
                # In parallel mode, follow all valid transitions
                for t in valid:
                    next_active.append(t.target)
                    self.prev[t.target] = node
            else:
                # In sequential mode, choose the transition with the highest target score
                best = max(valid, key=lambda t: t.target.score(prev_node, ctx))
                next_active.append(best.target)
                self.prev[best.target] = node

        # Update the list of currently active nodes
        self.active = next_active
