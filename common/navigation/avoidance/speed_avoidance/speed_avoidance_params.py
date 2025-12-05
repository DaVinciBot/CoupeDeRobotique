"""Parameters for the speed avoidance strategy."""

from __future__ import annotations

from navigation.avoidance.base_avoidance import BaseAvoidanceParams
from navigation.avoidance.structs import AvoidanceStrategy


class SpeedAvoidanceParams(BaseAvoidanceParams):
    """
    Parameters for the ``SPEED`` avoidance strategy.

    This strategy adapts the robot's avoidance timing based on its current
    speed profile (e.g., stopping distance, ACS detection, dynamic reaction
    time, etc.).

    """

    def __init__(
        self,
        timeout: float,
        avoidance_strategy: AvoidanceStrategy = AvoidanceStrategy.STOP_AND_WAIT,  # TODO: Change default to SPEED
        reaction_time: float = 0.2,
    ) -> None:
        """
        Initialize parameters for the speed-based avoidance strategy.

        Args:
        timeout : float
            Timeout in *seconds* before the strategy is considered failed
            or is reevaluated.
        avoidance_strategy : AvoidanceStrategy, optional
            The strategy identifier. Defaults to ``AvoidanceStrategy.SPEED``.
        reaction_time : float, optional
            The reaction delay (in seconds). Defaults to 0.2.
        """

        self.reaction_time = reaction_time
        super().__init__(avoidance_strategy, timeout * 1000.0)
