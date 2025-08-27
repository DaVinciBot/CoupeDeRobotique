"""Wrapper around generic navigation task for strategy use."""

from boombot_strategy.show_game_context import ShowGameContext
from navigation import TrajectoryPlanCommand
from strategy.core import BaseNavigationTask


class NavigationTask(BaseNavigationTask):
    """Thin wrapper exposing navigation to the strategy graph."""

    def handle(self, ctx: ShowGameContext) -> bool:
        """Execute the navigation plan and update the rolling basis.

        Args:
            ctx (ShowGameContext): The current game context.

        Returns:
            bool: ``True`` if the navigation task is finished, ``False`` otherwise.

        """
        if not self._is_initialized:
            self._initialize(ctx)

        cmd: TrajectoryPlanCommand = self.navigator_task.handle(
            ally_zone=ctx.arena.ally_zone,
            enemy_zone=ctx.arena.enemy_zone,
        )

        ctx.rolling_basis.set_target_position(cmd.get_position_command())
        self.logger.debug(f"[Navigation Task] State = {self.navigator_task.state}")
        return self.navigator_task.state.is_finished()
