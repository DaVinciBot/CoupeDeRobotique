from navigation import (
    TrajectoryPlanCommand,
)
from strategy.core import BaseNavigationTask
from boombot_strategy.show_game_context import ShowGameContext


class NavigationTask(BaseNavigationTask):
    def handle(self, ctx: ShowGameContext) -> bool:
        if not self._is_initialized:
            self._initialize(ctx)

        cmd: TrajectoryPlanCommand = self.navigator_task.handle(
            ally_zone=ctx.arena.ally_zone,
            enemy_zone=ctx.arena.enemy_zone,
        )

        ctx.rolling_basis.set_target_position(cmd.get_position_command())

        return self.navigator_task.state.is_finished()
