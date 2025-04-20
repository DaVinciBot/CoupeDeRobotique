from copy import deepcopy

from strategy import (
    BaseTaskNode,
    BaseTransition,
    GraphRunner,
    BasicTransition,
    ConditionalTransition,
)
from arena import ZoneAccessibility
from boombot_strategy.show_game_context import ShowGameContext
import boombot_strategy.strategies.common.go_to_stuff_zone as go_to_stuff_zone
import boombot_strategy.strategies.common.maneuver as maneuver
import boombot_strategy.strategies.yellow_strategies.tasks.go_to_yellow_zone as go_to_yellow_zone


# Pickup in zone 4, construct in zone 11
start = deepcopy(go_to_stuff_zone.go_to_zone_4_to_pickup)
go_to_zone_11_to_construct = deepcopy(go_to_yellow_zone.go_to_zone_11_to_construct)
quit_zone_11_after_construct = deepcopy(maneuver.quit_zone_after_construct)
start.add_transition(BasicTransition(target=go_to_zone_11_to_construct))
go_to_zone_11_to_construct.add_transition(
    BasicTransition(target=quit_zone_11_after_construct)
)

# Pickup in zone 2, construct in zone 10
go_to_stuff_zone_2 = deepcopy(go_to_stuff_zone.go_to_zone_2_to_pickup)
go_to_zone_10_to_construct = deepcopy(go_to_yellow_zone.go_to_zone_10_to_construct)
quit_zone_10_after_construct = deepcopy(maneuver.quit_zone_after_construct)
go_to_stuff_zone_2.add_transition(BasicTransition(target=go_to_zone_10_to_construct))
go_to_zone_10_to_construct.add_transition(
    BasicTransition(target=quit_zone_10_after_construct)
)

# Pickup in zone 3, construct in zone 11
go_to_stuff_zone_3 = deepcopy(go_to_stuff_zone.go_to_zone_3_to_pickup)
go_to_zone_11_to_construct = deepcopy(go_to_yellow_zone.go_to_zone_11_to_construct)
quit_zone_11_after_construct2 = deepcopy(maneuver.quit_zone_after_construct)
go_to_stuff_zone_3.add_transition(BasicTransition(target=go_to_zone_11_to_construct))
go_to_zone_11_to_construct.add_transition(
    BasicTransition(target=quit_zone_11_after_construct2)
)

# Link the tasks
quit_zone_11_after_construct.add_transition(
    ConditionalTransition(
        target=go_to_stuff_zone_2,
        condition=lambda current, target, ctx: ctx.arena.zones[2].accessibility
        != ZoneAccessibility.FREE,
    )
)
quit_zone_11_after_construct.add_transition(
    ConditionalTransition(
        target=go_to_stuff_zone_3,
        condition=lambda current, target, ctx: ctx.arena.zones[3].accessibility
        != ZoneAccessibility.FREE,
    )
)

quit_zone_10_after_construct.add_transition(
    ConditionalTransition(
        target=go_to_stuff_zone_3,
        condition=lambda current, target, ctx: ctx.arena.zones[3].accessibility
        != ZoneAccessibility.FREE,
    )
)

quit_zone_11_after_construct2.add_transition(
    ConditionalTransition(
        target=go_to_stuff_zone_2,
        condition=lambda current, target, ctx: ctx.arena.zones[2].accessibility
        != ZoneAccessibility.FREE,
    )
)


yellow_strategy = GraphRunner(start, parallel=False)
