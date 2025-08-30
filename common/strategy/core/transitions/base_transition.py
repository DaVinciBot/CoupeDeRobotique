"""Abstract base class for transitions between task nodes."""

from abc import ABC, abstractmethod

from strategy.core.base_game_context import BaseGameContext
from strategy.core.task_nodes.base_task_node import BaseTaskNode


class BaseTransition(ABC):
    """Abstract base class for representing a transition between task nodes.

    This class defines a common interface for all transition types. Subclasses
    must implement the ``can_transit`` method, which determines whether a
    transition is allowed based on the originating node and the game context.
    """

    def __init__(self, target: BaseTaskNode) -> None:
        """Initialize the transition with a target node.

        Args:
            target (BaseTaskNode): The destination node of the transition.

        """
        self.target = target

    @abstractmethod
    def can_transit(self, from_node: BaseTaskNode, ctx: BaseGameContext) -> bool:
        """Determine whether the transition should occur.

        Args:
            from_node (BaseTaskNode):
                The current task node attempting to transition.
            ctx (BaseGameContext): The current game context, which may include
                relevant state or conditions.

        Returns:
            bool: ``True`` if the transition should occur, ``False`` otherwise.

        """
