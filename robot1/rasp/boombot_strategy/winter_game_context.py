"""Game context used by the demo strategies."""

from __future__ import annotations

from typing import TYPE_CHECKING

from strategy.core import BaseGameContext

if TYPE_CHECKING:
    from services.spatial_computation import SpatialComputation, SpatialComputationDummy

    from arena.winter_arena import WinterArena
    from controllers.actuators import ActuatorsShow, ActuatorsShowDummy
    from controllers.rolling_basis import RollingBasis, RollingBasisDummy


class WinterGameContext(BaseGameContext):
    """Context class for the show game.

    This class is used to store the context of the show game.
    """

    def __init__(
        self,
        arena: WinterArena,
        rolling_basis: RollingBasis | RollingBasisDummy,
        actuators: ActuatorsShow | ActuatorsShowDummy,
        spatial_computation: SpatialComputation | SpatialComputationDummy,
        score: int = 0,
    ) -> None:
        """Initialize the WinterGameContext.

        Args:
            arena (WinterArena): The arena of the game.
            rolling_basis (RollingBasis | RollingBasisDummy):
                The rolling basis of the robot.
            actuators (ActuatorsShow | ActuatorsShowDummy): The actuators of the robot.
            score (int, optional): The score of the robot. Defaults to 0.
        """
        super().__init__(arena)
        self.rolling_basis: RollingBasis | RollingBasisDummy = rolling_basis
        self.actuators: ActuatorsShow | ActuatorsShowDummy = actuators
        self.spatial_computation: SpatialComputation | SpatialComputationDummy = (
            spatial_computation
        )
        self.score = score
