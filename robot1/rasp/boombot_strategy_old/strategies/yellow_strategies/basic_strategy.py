from copy import deepcopy

from strategy import BaseTaskNode, BaseTransition, GraphRunner, BasicTransition, ConditionalTransition
from arena import ZoneAccessibility
from boombot_strategy_old.show_game_context import ShowGameContext
import boombot_strategy_old.strategies.common.go_to_stuff_zone as go_to_stuff_zone
import boombot_strategy_old.strategies.common.maneuver as maneuver
import boombot_strategy_old.strategies.yellow_strategies.tasks.go_to_yellow_zone as go_to_yellow_zone
from boombot_strategy_old.sub_graph import ConstructSubGraph

from strategy import BaseTaskNode, BaseTransition, GraphRunner, BasicTransition
from boombot_strategy_old.task import GoToStuffZoneToPickUp


go_to_pick_4 = BaseTaskNode(
    name="Go to zone 4 to pickup", task=GoToStuffZoneToPickUp(4)
)
go_to_pick_3 = BaseTaskNode(
    name="Go to zone 3 to pickup", task=GoToStuffZoneToPickUp(3)
)
go_to_pick_2 = BaseTaskNode(
    name="Go to zone 2 to pickup", task=GoToStuffZoneToPickUp(2)
)

construct_11 = ConstructSubGraph(zone_to_construct_id=11)
construct_10 = ConstructSubGraph(zone_to_construct_id=10)

# Links
go_to_pick_4.add_transition(BasicTransition(target=construct_11.start))
construct_11.end.add_transition(
    ConditionalTransition(
        target=go_to_pick_3,
        condition=lambda current, target, ctx: ctx.arena.zones[3].accessibility != ZoneAccessibility.FREE,
    )
)
construct_11.end.add_transition(
    ConditionalTransition(
        target=go_to_pick_2,
        condition=lambda current, target, ctx: ctx.arena.zones[2].accessibility != ZoneAccessibility.FREE,
    )
)

go_to_pick_3.add_transition(BasicTransition(target=construct_10.start))
go_to_pick_2.add_transition(BasicTransition(target=construct_10.start))



from strategy.visualize import visualize_task_graph
visualize_task_graph(go_to_pick_4, "yellow_strategy", view=True)

yellow_strategy = GraphRunner(go_to_pick_4, parallel=False)

