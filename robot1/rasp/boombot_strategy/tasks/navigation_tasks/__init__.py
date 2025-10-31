"""Navigation task implementations for Boombot strategies."""

from boombot_strategy.tasks.navigation_tasks.go_to_color_reserved_zone import (
    GoToColorReservedZoneToConstruct,
    GoToColorReservedZoneToFinishGame,
)
from boombot_strategy.tasks.navigation_tasks.go_to_stuff_zone import (
    GoToStuffZoneToPickUp,
)
from boombot_strategy.tasks.navigation_tasks.maneuver import (
    GoCentroidOfZone,
    RelativeBackward,
    RelativeForward,
)
from boombot_strategy.tasks.navigation_tasks.navigation_task import NavigationTask
from boombot_strategy.tasks.navigation_tasks.odometrie import SetOdometrie

__all__ = [
    "GoCentroidOfZone",
    "GoToColorReservedZoneToConstruct",
    "GoToColorReservedZoneToFinishGame",
    "GoToStuffZoneToPickUp",
    "NavigationTask",
    "RelativeBackward",
    "RelativeForward",
    "SetOdometrie",
    "Recalage",
]
