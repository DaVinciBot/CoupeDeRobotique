"""Tasks for resetting or adjusting robot odometry."""

from __future__ import annotations

from typing import override

from boombot_strategy.show_game_context import ShowGameContext
from geometry import OrientedPoint
from strategy.core.tasks.base_task import BaseTask


class SetOdometrie(BaseTask[ShowGameContext]):
    """Task to update the robot's odometry position.

    The task uses the provided ``x``, ``y`` and ``theta`` values if given;
    otherwise it falls back to the current values from the ally zone.
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
        # Get the current position from the ally zone
        current_position: OrientedPoint = ctx.arena.ally_zone.point

        # Create new position using provided values or current ones as fallback
        new_position = OrientedPoint(
            self.x if self.x is not None else current_position.x,
            self.y if self.y is not None else current_position.y,
            self.theta if self.theta is not None else current_position.theta,
        )

        # Update odometry with the new position
        ctx.rolling_basis.set_odometrie(new_position)

        return True
