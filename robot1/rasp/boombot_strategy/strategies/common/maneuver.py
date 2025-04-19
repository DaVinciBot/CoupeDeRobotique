from strategy import BaseTaskNode
from boombot_strategy.task import BackwardToQuitConstruction


quit_zone_after_construct = BaseTaskNode(
    name="Quit zone after construction",
    task=BackwardToQuitConstruction(),
)
