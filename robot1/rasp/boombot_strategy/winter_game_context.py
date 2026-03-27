"""Game context used by the demo strategies."""

from __future__ import annotations

from typing import TYPE_CHECKING

from strategy.core import BaseGameContext

if TYPE_CHECKING:
    from arena.winter_arena import WinterArena
    from controllers.actuators import ActuatorsWinter, ActuatorsWinterDummy
    from controllers.rolling_basis import RollingBasis, RollingBasisDummy


class WinterGameContext(BaseGameContext):
    """Context class for the show game.

    This class is used to store the context of the show game.
    """

    def __init__(
        self,
        arena: WinterArena,
        rolling_basis: RollingBasis | RollingBasisDummy,
        actuators: ActuatorsWinter | ActuatorsWinterDummy,
        point: int = 0,
    ) -> None:
        """Initialize the WinterGameContext.

        Args:
            arena (WinterArena): The arena of the game.
            rolling_basis (RollingBasis | RollingBasisDummy):
                The rolling basis of the robot.
            actuators (ActuatorsWinter | ActuatorsWinterDummy):
                The actuators of the robot.
            point (int, optional): The score of the robot. Defaults to 0.
        """
        super().__init__(arena)
        self.rolling_basis: RollingBasis | RollingBasisDummy = rolling_basis
        self.actuators: ActuatorsWinter | ActuatorsWinterDummy = actuators
        self.point = point
