"""Wrapper around generic navigation task for strategy use."""

from __future__ import annotations

from typing import TYPE_CHECKING, override

from boombot_strategy.show_game_context import ShowGameContext
from strategy.core.tasks import BaseNavigationTask

if TYPE_CHECKING:
    from navigation.trajectory_planner import TrajectoryPlanCommand


class NavigationTask(BaseNavigationTask[ShowGameContext]):
    """Thin wrapper exposing navigation to the strategy graph."""

    @override
    def handle(self, ctx: ShowGameContext) -> bool:
        """Execute the navigation plan and update the rolling basis.

        Args:
            ctx (ShowGameContext): The current game context.

        Returns:
            bool: ``True`` if the navigation task is finished, ``False`` otherwise.
        """
        if not self._is_initialized:
            self._initialize(ctx)

        ctx.arena.ally_zone.update(
            ctx.arena.team_color,
            ctx.rolling_basis.odometrie,
            ctx.arena.enemy_zone.point,
        )

        cmd: TrajectoryPlanCommand = self.navigator_task.handle(
            ally_zone=ctx.arena.ally_zone,
            enemy_zone=ctx.arena.enemy_zone,
        )

        ctx.rolling_basis.set_target_position(cmd.get_position_command())
        self.logger.debug(f"[Navigation Task] {cmd.get_full_command()}")
        self.logger.debug(f"[Navigation Task] State = {self.navigator_task.state}")
        return self.navigator_task.state.is_finished()
