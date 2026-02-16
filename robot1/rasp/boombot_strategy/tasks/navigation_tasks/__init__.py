"""Navigation task implementations for Boombot strategies."""

from boombot_strategy.tasks.navigation_tasks.go_to_color_reserved_zone import (
    GoToColorReservedZoneToDeposit,
    GoToColorReservedZoneToFinishGame,
)
from boombot_strategy.tasks.navigation_tasks.go_to_stuff_zone import (
    GoToStuffZoneToPickUp,
)

from boombot_strategy.tasks.navigation_tasks.go_to_deposit_zone import (
    GoToDepositZone,
)

from boombot_strategy.tasks.navigation_tasks.maneuver import (
    GoCentroidOfZone,
    GoToOrientedPoint,
    RelativeBackward,
    RelativeForward,
)
from boombot_strategy.tasks.navigation_tasks.navigation_task import NavigationTask
from boombot_strategy.tasks.navigation_tasks.odometrie import SetOdometrie

__all__ = [
    "GoCentroidOfZone",
    "GoToColorReservedZoneToDeposit",
    "GoToColorReservedZoneToFinishGame",
    "GoToDepositZone",
    "GoToOrientedPoint",
    "GoToStuffZoneToPickUp",
    "NavigationTask",
    "RelativeBackward",
    "RelativeForward",
    "SetOdometrie",
]
