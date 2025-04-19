from strategy import BaseTaskNode
from boombot_strategy.task import (
    GoToColorReservedZoneToFinishGame,
    GoToColorReservedZoneToConstruct,
)


# Go to Yellow Zone to construct
go_to_zone_10_to_construct = BaseTaskNode(
    name="Go to zone 10 to construct",
    task=GoToColorReservedZoneToConstruct(10),
)
go_to_zone_11_to_construct = BaseTaskNode(
    name="Go to zone 11 to construct",
    task=GoToColorReservedZoneToConstruct(11),
)
go_to_zone_12_to_construct = BaseTaskNode(
    name="Go to zone 12 to construct",
    task=GoToColorReservedZoneToConstruct(12),
)
go_to_zone_13_to_construct = BaseTaskNode(
    name="Go to zone 13 to construct",
    task=GoToColorReservedZoneToConstruct(13),
)

# Go to Yellow Zone to finish game (back to home)
go_to_zone_10_to_finish_game = BaseTaskNode(
    name="Go to zone 10 to finish game",
    task=GoToColorReservedZoneToFinishGame(10),
)
go_to_zone_11_to_finish_game = BaseTaskNode(
    name="Go to zone 11 to finish game",
    task=GoToColorReservedZoneToFinishGame(11),
)
go_to_zone_12_to_finish_game = BaseTaskNode(
    name="Go to zone 12 to finish game",
    task=GoToColorReservedZoneToFinishGame(12),
)
go_to_zone_13_to_finish_game = BaseTaskNode(
    name="Go to zone 13 to finish game",
    task=GoToColorReservedZoneToFinishGame(13),
)
