"""Base parameters shared by avoidance strategies."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from navigation.avoidance.structs import AvoidanceStrategy


class BaseAvoidanceParams:
    """Base class for common parameters used in avoidance strategies.

    This class serves as a container for configuration values such as the
    avoidance strategy type and an optional timeout duration.

    """

    def __init__(
        self,
        avoidance_strategy: AvoidanceStrategy,
        timeout: float | None = None,
    ) -> None:
        """Initialize the base avoidance parameters.

        Args:
            avoidance_strategy (AvoidanceStrategy):
                The selected avoidance strategy.
            timeout (float | None, optional):
                Optional timeout for the avoidance procedure.

        """
        self.avoidance_strategy: AvoidanceStrategy = avoidance_strategy
        self.timeout: float | None = timeout
