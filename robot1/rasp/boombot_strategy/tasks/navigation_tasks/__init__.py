from boombot_strategy.tasks.navigation_tasks.navigation_task import NavigationTask

from boombot_strategy.tasks.navigation_tasks.go_to_color_reserved_zone import (
    GoToColorReservedZoneToFinishGame,
    GoToColorReservedZoneToConstruct,
)

from boombot_strategy.tasks.navigation_tasks.go_to_stuff_zone import (
    GoToStuffZoneToPickUp,
)

from boombot_strategy.tasks.navigation_tasks.odometrie import (
    SetOdometrie,
)

from boombot_strategy.tasks.navigation_tasks.maneuver import (
    RelativeForward,
    RelativeBackward,
    GoCentroidOfZone,
)
