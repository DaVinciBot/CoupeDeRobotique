"""Tasks for resetting or adjusting robot odometry."""

from __future__ import annotations

from typing import override

from boombot_strategy.show_game_context import ShowGameContext
from geometry import OrientedPoint
from strategy.core.tasks.base_task import BaseTask


class SetOdometrie(BaseTask[ShowGameContext]):
    """Task to update the robot's odometry position.

    The task uses the provided ``x``, ``y`` and ``theta`` values if given;
    otherwise it falls back to the current values from the rolling basis.
    After updating the odometry, the arena's ally zone is synchronized.
    """

    def __init__(
        self,
        x: float | None = None,
        y: float | None = None,
        theta: float | None = None,
    ) -> None:
        """Initialize the SetOdometrie task with optional position values.

        Args:
            x (float | None, optional): X coordinate. Defaults to None.
            y (float | None, optional): Y coordinate. Defaults to None.
            theta (float | None, optional): Orientation in radians. Defaults to None.
        """
        self.x: float | None = x
        self.y: float | None = y
        self.theta: float | None = theta

        super().__init__()

    @override
    def handle(self, ctx: ShowGameContext) -> bool:
        """Handle the execution of the odometry setting task.

        Args:
            ctx (ShowGameContext): Context containing game state and arena info.

        Returns:
            bool: Always returns ``True`` after setting the new odometry.
        """
        # CRITICAL: Get current position from rolling_basis.odometrie
        # (not arena.ally_zone.point) because arena.ally_zone.point may be outdated
        current_position: OrientedPoint = ctx.rolling_basis.odometrie

        # Create new position using provided values or current ones as fallback
        new_position = OrientedPoint(
            self.x if self.x is not None else current_position.x,
            self.y if self.y is not None else current_position.y,
            self.theta if self.theta is not None else current_position.theta,
        )

        # Update rolling basis odometry
        ctx.rolling_basis.set_odometrie(new_position)

        # Synchronize arena.ally_zone with the new odometry
        ctx.arena.ally_zone.update(
            ctx.arena.team_color,
            new_position,
            ctx.arena.enemy_zone.point,
        )

        return True


class WallSetOdometrie(BaseTask[ShowGameContext]):
    """Task to reset odometry based on the closest wall goal at runtime."""

    def __init__(self) -> None:
        super().__init__()

    @override
    def handle(self, ctx: ShowGameContext) -> bool:
        """Handle the execution of the wall-based odometry reset task.
        Args:
            ctx (ShowGameContext): Context containing game state and arena info.
        Returns:
            bool: Returns SetOdometrie task result or True if no wall goal found.
        """
        goal: OrientedPoint | None = ctx.arena.get_closest_wall_goal()
        if goal is None:
            ctx.logger.warning("[Resetting] get_closest_wall_goal returned None — skipping odometry reset")
            return True

        return SetOdometrie(goal.x, goal.y, goal.theta).handle(ctx)
