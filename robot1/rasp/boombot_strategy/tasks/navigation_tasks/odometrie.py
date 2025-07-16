# ====== Code Summary ======
# This module defines a task class `SetOdometrie` that updates the robot's odometry
# based on optionally provided coordinates (x, y, theta). If any coordinate is not
# provided, it defaults to the current position from the game context.

from boombot_strategy.show_game_context import ShowGameContext
from geometry import OrientedPoint
from strategy.core.tasks.base_task import BaseTask


class SetOdometrie(BaseTask):
    """Task to set or update the robot's odometry position based on the given
    coordinates (x, y, theta). If any of the coordinates are not provided,
    the current value from the ally zone will be used instead.

    Attributes:
        x (float | None): Optional X coordinate.
        y (float | None): Optional Y coordinate.
        theta (float | None): Optional orientation (in radians).
    """

    def __init__(
        self,
        x: float | None = None,
        y: float | None = None,
        theta: float | None = None,
    ):
        """Initialize the SetOdometrie task with optional position values.

        Args:
            x (float | None): Optional X coordinate.
            y (float | None): Optional Y coordinate.
            theta (float | None): Optional orientation in radians.
        """
        self.x: float | None = x
        self.y: float | None = y
        self.theta: float | None = theta

        super().__init__()

    def handle(self, ctx: ShowGameContext) -> bool:
        """Handle the execution of the odometry setting task.

        Args:
            ctx (ShowGameContext): Context containing game state and arena info.

        Returns:
            bool: Always returns True after setting the new odometry.
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
