from strategy import BaseTaskNode, BaseTransition, GraphRunner, BasicTransition
from boombot_strategy.task import GoToStuffZoneToPickUp

# Go to Stuff Zone to pick up
go_to_zone_0_to_pickup = BaseTaskNode(
    name="Go to zone 0 to pickup", task=GoToStuffZoneToPickUp(0)
)
go_to_zone_1_to_pickup = BaseTaskNode(
    name="Go to zone 1 to pickup", task=GoToStuffZoneToPickUp(1)
)
go_to_zone_2_to_pickup = BaseTaskNode(
    name="Go to zone 2 to pickup", task=GoToStuffZoneToPickUp(2)
)
go_to_zone_3_to_pickup = BaseTaskNode(
    name="Go to zone 3 to pickup", task=GoToStuffZoneToPickUp(3)
)
go_to_zone_4_to_pickup = BaseTaskNode(
    name="Go to zone 4 to pickup", task=GoToStuffZoneToPickUp(4)
)
go_to_zone_5_to_pickup = BaseTaskNode(
    name="Go to zone 5 to pickup", task=GoToStuffZoneToPickUp(5)
)
go_to_zone_6_to_pickup = BaseTaskNode(
    name="Go to zone 6 to pickup", task=GoToStuffZoneToPickUp(6)
)
go_to_zone_7_to_pickup = BaseTaskNode(
    name="Go to zone 7 to pickup", task=GoToStuffZoneToPickUp(7)
)
go_to_zone_8_to_pickup = BaseTaskNode(
    name="Go to zone 8 to pickup", task=GoToStuffZoneToPickUp(8)
)
go_to_zone_9_to_pickup = BaseTaskNode(
    name="Go to zone 9 to pickup", task=GoToStuffZoneToPickUp(9)
)
