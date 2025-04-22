from typing import List, Dict, Optional
from strategy.core.task_nodes.base_task_node import BaseTaskNode
from strategy.core.transitions.base_transition import BaseTransition
from strategy.core.base_game_context import BaseGameContext
from loggerplusplus import Logger


class GraphRunner:
    def __init__(
        self, start: BaseTaskNode, logger: Logger, parallel: bool = False
    ) -> None:
        self.logger = logger
        self.parallel = parallel
        self.active: List[BaseTaskNode] = [start]
        self.prev: Dict[BaseTaskNode, Optional[BaseTaskNode]] = {start: None}

    def handle(self, ctx: BaseGameContext) -> None:
        next_active: List[BaseTaskNode] = []

        for node in self.active:
            prev_node = self.prev.get(node)

            if not node._entered:
                self.logger.info(
                    f"==> Entering node: {node.name} [{node.tasks[0].__class__.__name__ if node.tasks else 'NoTask'}]"
                )

            done = node.handle(ctx)

            if not done:
                self.logger.debug(f"  ... still executing: {node.name}")
                next_active.append(node)
                continue

            self.logger.info(f"==> Finished node: {node.name}")

            valid: List[BaseTransition] = [
                t
                for t in node.transitions
                if t.can_transit(from_node=prev_node, ctx=ctx)
            ]

            if not valid:
                self.logger.info(
                    f"    No valid transitions from {node.name}. End of branch."
                )
                continue

            if self.parallel:
                for t in valid:
                    self.logger.info(
                        f"    {node.name} -> {t.target.name} via {t.__class__.__name__}"
                    )
                    next_active.append(t.target)
                    self.prev[t.target] = node
            else:
                best = max(valid, key=lambda t: t.target.score(prev_node, ctx))
                score_value = best.target.score(prev_node, ctx)
                self.logger.info(
                    f"    {node.name} -> {best.target.name} via {best.__class__.__name__} (score: {score_value:.2f})"
                )
                next_active.append(best.target)
                self.prev[best.target] = node

        self.active = next_active
