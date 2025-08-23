from typing import override

from strategy.core.base_game_context import BaseGameContext
from strategy.core.tasks.base_task import BaseTask


class FakeTask(BaseTask):
    @override
    def handle(self, ctx: BaseGameContext) -> bool:
        return True
