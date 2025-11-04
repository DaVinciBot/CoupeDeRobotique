"""Common library for CoupeDeRobotique.

This package groups core building blocks reused by all robots:
- arena: arena models, zones and grid managers
- geometry: geometric helpers and primitives
- gpio: GPIO abstraction and dummies
- led_strip: LED strip helpers
- navigation: avoidance, path/trajectory planners, navigator core
- strategy: graph runner, tasks, scoring, transitions
- teensy: Teensy communication and GPIO manager
- usb_com: USB serial protocols (C++/Python) and tools
- utils: misc utilities
- video: streaming/server utilities

Public API: `arena`, `geometry`, `gpio`, `led_strip`, `navigation`,
`strategy`, `teensy`, `usb_com`, `utils`, `video`.
"""

from . import (
    arena,
    calcul_deporte,
    geometry,
    gpio,
    led_strip,
    navigation,
    strategy,
    teensy,
    usb_com,
    utils,
    video,
)

__all__ = [
    "arena",
    "calcul_deporte",
    "geometry",
    "gpio",
    "led_strip",
    "navigation",
    "strategy",
    "teensy",
    "usb_com",
    "utils",
    "video",
]
