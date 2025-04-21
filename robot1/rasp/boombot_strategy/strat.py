from strategy.core import (
    SubGraphBuilder,
    BaseTaskNode,
    DirectTransition,
    ConditionalTransition,
    BaseSubGraph,
    BaseTask,
    BaseTransitionCondition,
FakeTask
)

from strategy.tools import (
    visualize_task_graph_from_node,
)
from boombot_strategy.show_game_context import ShowGameContext
from boombot_strategy.tasks import GoToStuffZoneToPickUp

from arena import ZoneAccessibility


class IsNotFreeZone(BaseTransitionCondition):
    def __init__(self, zone_to_check: int):
        self.zone_to_check = zone_to_check

    def check(
        self, from_node: BaseTaskNode, next_node: BaseTaskNode, ctx: ShowGameContext
    ) -> bool:
        return (
            ctx.arena.zones[self.zone_to_check].accessibility != ZoneAccessibility.FREE
        )


# === Pipeline 1 ===
builder1 = SubGraphBuilder()
builder1.add_node("A", BaseTaskNode("A", GoToStuffZoneToPickUp(0)))
builder1.add_node("B", BaseTaskNode("B", GoToStuffZoneToPickUp(1)))

builder1.add_node("C", BaseTaskNode("C", GoToStuffZoneToPickUp(2)))
builder1.add_node("D", BaseTaskNode("D", GoToStuffZoneToPickUp(3)))

builder1.add_node("Aiguillage", BaseTaskNode("Aiguillage", FakeTask()))

builder1.connect("A", DirectTransition(builder1.nodes["B"]))
builder1.connect(
    "B",
    ConditionalTransition(
        builder1.nodes["C"],
        IsNotFreeZone(2),
    ),
)
builder1.connect(
    "B",
    ConditionalTransition(
        builder1.nodes["D"],
        IsNotFreeZone(3),
    ),
)

builder1.connect("D", DirectTransition(builder1.nodes["Aiguillage"]))
builder1.connect("C", DirectTransition(builder1.nodes["Aiguillage"]))

sub1 = builder1.build(entry="A", exits="Aiguillage")


visualize_task_graph_from_node(
    start_node=sub1.get_entry(),
    title="Subgraph 1",
)
