"""Robot1 application package.

Main components:
- rasp: runtime app (brains, controllers, sensors, strategies, WebUI, entrypoints)
  - rasp.boombot_strategy: strategies, tasks, sub-graphs
  - rasp.brains: high-level brain orchestration
  - rasp.controllers: actuators & rolling basis controllers
  - rasp.sensors: LIDAR, inputs
"""

from . import rasp

__all__ = [
    "rasp",
]
