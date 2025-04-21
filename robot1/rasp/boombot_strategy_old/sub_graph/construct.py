from strategy import BaseSubGraph, BaseTaskNode, BasicTransition
from boombot_strategy_old.task import (
    GoToColorReservedZoneToConstruct,
    BackwardToQuitConstruction,
)


class ConstructSubGraph(BaseSubGraph):
    """
    SubGraph for the construction tasks.
    """

    def __init__(self, zone_to_construct_id: int) -> None:
        n0 = BaseTaskNode(
            name=f"Go to zone {zone_to_construct_id} to construct",
            task=GoToColorReservedZoneToConstruct(
                color_reserved_zone_id=zone_to_construct_id,
            ),
        )
        n1 = BaseTaskNode(
            name="Backward to quit construction",
            task=BackwardToQuitConstruction(),
        )

        n0.add_transition(BasicTransition(target=n1))

        super().__init__(
            start=n0,
            end=n1,
        )
