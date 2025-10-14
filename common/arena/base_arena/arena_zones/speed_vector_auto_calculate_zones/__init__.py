"""Zones that auto-calculate speed vectors based on enemy movement."""

# ruff: noqa: E501

from arena.base_arena.arena_zones.speed_vector_auto_calculate_zones.base_speed_vector_auto_calculate_zone import (
    BaseSpeedVectorAutoCalculateZone,
)
from arena.base_arena.arena_zones.speed_vector_auto_calculate_zones.enemy_zone import (
    EnemyZone,
)

__all__ = [
    "BaseSpeedVectorAutoCalculateZone",
    "EnemyZone",
]
