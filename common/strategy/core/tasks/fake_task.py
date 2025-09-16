"""Simple task implementation used for testing."""

from __future__ import annotations

from typing import override

from strategy.core.base_game_context import BaseGameContext
from strategy.core.tasks.base_task import BaseTask


class FakeTask(BaseTask[BaseGameContext]):
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
