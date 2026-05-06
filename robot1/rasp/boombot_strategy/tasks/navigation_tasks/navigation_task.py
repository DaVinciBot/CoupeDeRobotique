"""Wrapper around generic navigation task for strategy use."""

from __future__ import annotations

from typing import TYPE_CHECKING, override

from a_config_loader import CONFIG
from boombot_strategy.winter_game_context import WinterGameContext
from navigation.navigator.task.states import NavigatorTaskState
from strategy.core.tasks import BaseNavigationTask

if TYPE_CHECKING:
    from navigation.trajectory_planner import TrajectoryPlanCommand


def simulation_delay(default: float) -> float:
    return 0.05 if CONFIG.ROLLING_BASIS_DUMMY else default


def simulation_step_sleep_delay(default: float) -> float:
    return 0.0 if CONFIG.ROLLING_BASIS_DUMMY else default


class NavigationTask(BaseNavigationTask[WinterGameContext]):
    """Thin wrapper exposing navigation to the strategy graph."""

    def _refresh_path_planner_grid(self, ctx: WinterGameContext) -> None:
        if hasattr(self.path_planner_params, "grid"):
            self.path_planner_params.grid = (
                ctx.arena.grid_manager.get_static_and_dynamic_grid()
            )
        if self._is_initialized and hasattr(
            self.navigator_task.path_planner.params,
            "grid",
        ):
            self.navigator_task.path_planner.params.grid = (
                ctx.arena.grid_manager.get_static_and_dynamic_grid()
            )

    @override
    def handle(self, ctx: WinterGameContext) -> bool:
        """Execute the navigation plan and update the rolling basis.

        Args:
            ctx (WinterGameContext): The current game context.

        Returns:
            bool: ``True`` if the navigation task is finished, ``False`` otherwise.
        """
        self._refresh_path_planner_grid(ctx)
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
        self._logger.debug(f"[TASK:Nav] {cmd.get_full_command()}")
        self._logger.debug(f"[TASK:Nav] State: {self.navigator_task.state}")
        if self.navigator_task.state == NavigatorTaskState.ABORT:
            msg = f"Navigation aborted before reaching {self.goal}"
            raise RuntimeError(msg)
        return self.navigator_task.state.is_finished()
