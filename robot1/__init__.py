"""Robot1 application package.

Main components:
- rasp: runtime app (brains, controllers, sensors, strategies, WebUI, entrypoints)
  - rasp.botladyyy_strategy: strategies, tasks, sub-graphs
  - rasp.brains: high-level brain orchestration
  - rasp.controllers: actuators & rolling basis controllers
  - rasp.sensors: LIDAR, inputs
"""

from robot1 import rasp

__all__ = [
    "rasp",
]
