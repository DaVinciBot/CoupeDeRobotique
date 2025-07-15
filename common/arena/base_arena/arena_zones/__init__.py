# ====== Struct and Enum ======
from arena.base_arena.arena_zones.structs import (
    ZoneAccessibility,
    ZoneType,
)

# ====== Base Zone Import ======
from arena.base_arena.arena_zones.base_arena_zone import BaseArenaZone

# ====== Derived Zone Imports ======
# Level 1 derivatives zones: simple ones
from arena.base_arena.arena_zones.forbidden_zone import ForbiddenZone
from arena.base_arena.arena_zones.border_zone import BorderZone
from arena.base_arena.arena_zones.stuff_zone import StuffZone
from arena.base_arena.arena_zones.ally_zone import AllyZone

# Level 2 derivatives zones: more complex ones
# 1.Colored reserved zones
# Base class
from arena.base_arena.arena_zones.color_reserved_zones import BaseColorReservedZone

# Derived classes
from arena.base_arena.arena_zones.color_reserved_zones import BlueReservedZone
from arena.base_arena.arena_zones.color_reserved_zones import YellowReservedZone

# 2.Auto speed vector zones
# Base class
from arena.base_arena.arena_zones.speed_vector_auto_calculate_zones import (
    BaseSpeedVectorAutoCalculateZone,
)

# Derived classes
from arena.base_arena.arena_zones.speed_vector_auto_calculate_zones import EnemyZone


__all__ = [
    "AllyZone",
    "BaseArenaZone",
    "BaseColorReservedZone",
    "BaseSpeedVectorAutoCalculateZone",
    "BlueReservedZone",
    "BorderZone",
    "EnemyZone",
    "ForbiddenZone",
    "StuffZone",
    "YellowReservedZone",
    "ZoneAccessibility",
    "ZoneType",
]
