"""Simple task implementation used for testing."""

from __future__ import annotations

from typing import TYPE_CHECKING, override

from strategy.core.tasks.base_task import BaseTask

if TYPE_CHECKING:
    from strategy.core.base_game_context import BaseGameContext


class FakeTask(BaseTask):
    """Trivial task that immediately succeeds."""

    @override
    def handle(self, ctx: BaseGameContext) -> bool:
        """Return ``True`` without performing any action.

        Args:
            ctx (BaseGameContext): The game context.

        Returns:
            bool: ``True``.
        """
        return True
