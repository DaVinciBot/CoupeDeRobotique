from strategy import BaseTaskNode
from boombot_strategy_old.task import BackwardToQuitConstruction


quit_zone_after_construct = BaseTaskNode(
    name="Quit zone after construction",
    task=BackwardToQuitConstruction(),
)
