from strategy.core.tasks.base_task import BaseTask
from strategy.core.base_game_context import BaseGameContext


class FakeTask(BaseTask):

    def handle(self, ctx: BaseGameContext) -> bool:
        return True
