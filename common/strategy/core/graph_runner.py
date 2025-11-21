"""Execution engine for strategy graphs."""

from __future__ import annotations

from typing import TYPE_CHECKING

from log_manager import LogLogger

if TYPE_CHECKING:
    from loggerplusplus import Logger

    from strategy.core.base_game_context import BaseGameContext
    from strategy.core.task_nodes.base_task_node import BaseTaskNode


class GraphRunner:
    """Execute a graph of task nodes."""

    def __init__(
        self,
        start: BaseTaskNode,
        logger: Logger | None = None,
        *,
        parallel: bool = False,
    ) -> None:
        """Create a new :class:``GraphRunner``.

        Args:
            start (BaseTaskNode): The entry node for the graph.
            logger (Logger | None, optional):
                Logger instance for debugging. Defaults to None.
            parallel (bool, optional): Execute all valid transitions in parallel when
                ``True``. Defaults to ``False``.
        """
        self._logger = logger or LogLogger(
            identifier="GraphRunner",
            follow_logger_manager_rules=True,
        )
        self.parallel = parallel
        self.active: list[BaseTaskNode] = [start]
        self.prev: dict[BaseTaskNode, BaseTaskNode | None] = {start: None}
        self._logger.info(
            f"[STRAT] GraphRunner initialized with start: '{start.name}', "
            f"parallel={self.parallel}",
        )

    def handle(self, ctx: BaseGameContext) -> None:
        """Advance the graph execution by one step.

        Args:
            ctx (BaseGameContext): Context passed to each node.
        """
        if not self.active:
            self._logger.warning(
                "[STRAT] No active nodes - execution complete or not started",
            )
            return

        next_active: list[BaseTaskNode] = []
        for node in self.active:
            prev_node = self.prev.get(node)

            # Log entry if first time
            if not node.entered:
                task_name = node.tasks[0].__class__.__name__ if node.tasks else "NoTask"
                self._logger.info(f"[STRAT] ==> Entering: {node.name} [{task_name}]")

            done = node.handle(ctx)
            if not done:
                self._logger.debug(f"[STRAT] ... executing: {node.name}")
                next_active.append(node)
                continue

            # Node completed
            self._logger.info(
                f"[STRAT] <== Finished: {node.name} with status {node.status.name}",
            )

            # Gather valid transitions
            valid_transitions = [
                t
                for t in node.transitions
                if t.can_transit(from_node=prev_node, ctx=ctx)
                and t.target not in self.prev.items()
            ]
            if not valid_transitions:
                msg = (
                    f"[STRAT]     No valid transitions from '{node.name}' - branch ends"
                )
                self._logger.info(msg)
                continue

            if self.parallel:
                for transition in valid_transitions:
                    target = transition.target
                    msg = (
                        f"[STRAT]     Transition: '{node.name}' -> '{target.name}' "
                        f"via {transition.__class__.__name__}"
                    )
                    self._logger.info(msg)
                    next_active.append(target)
                    self.prev[target] = node
            else:
                # Choose the transition leading to the highest-scoring node
                best = max(
                    valid_transitions,
                    key=lambda t, prev=prev_node: t.target.score(prev, ctx),
                )
                score_val = best.target.score(prev_node, ctx)
                target = best.target
                msg = (
                    f"[STRAT]     Chosen: '{node.name}' -> '{target.name}' "
                    f"via {best.__class__.__name__} (score={score_val:.2f})"
                )
                self._logger.info(msg)
                next_active.append(target)
                self.prev[target] = node

        self.active = next_active

    def run(self, ctx: BaseGameContext, max_steps: int = 1000) -> None:
        """Run the graph until completion or until ``max_steps`` iterations.

        Args:
            ctx (BaseGameContext): Game context passed to task nodes.
            max_steps (int, optional):
                Safety limit to prevent infinite loops. Defaults to 1000.
        """
        step = 0
        while self.active and step < max_steps:
            active_names = [n.name for n in self.active]
            msg = f"[STRAT] Step {step + 1}, active: {active_names}"
            self._logger.debug(msg)
            self.handle(ctx)
            step += 1
        if self.active:
            remaining = [n.name for n in self.active]
            msg = (
                f"[STRAT] Max steps reached ({max_steps}) - "
                f"active nodes remaining: {remaining}"
            )
            self._logger.warning(msg)
        else:
            self._logger.info("[STRAT] All nodes completed")
