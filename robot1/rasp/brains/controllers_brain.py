# External imports
import asyncio

# Import from common
from config_loader import CONFIG

from taskbrain import Brain

from config_loader import CONFIG

# External imports
import asyncio
import time

# Import from common
from taskbrain import Brain
from ws_comms import WSmsg, WSclientRouteManager, WServerRouteManager
from geometry import OrientedPoint, Point, distance, Polygon, MultiPoint

from loggerplusplus import Logger
import math
from utils import Utils
import matplotlib.pyplot as plt
import time
import numpy as np
import random

# Import from local path
from controllers import RollingBasis, RollingBasisDummy

from path_finding import PathFinder
from arena import ShowArena
from rolling_basis_handler import RollingBasisHandler, RollingBasisCommand
from movement_manager import MovementManager, GoToParams, MovementStatus
from rolling_basis_handler import SpeedProfile
from sensors import Lidar, LidarDummy
from arena import AllyZone


@Brain.task(process=True, run_on_start=True, refresh_rate=0.1, define_loop_later=True)
def handle_movement_manager(self) -> None:
    movement_manager = MovementManager(
        logger=Logger(
            identifier="MovementManager",
            follow_logger_manager_rules=True,
        ),
        rolling_basis_handler_logger=Logger(
            identifier="RollingBasisHandler",
            follow_logger_manager_rules=True,
        ),
        path_finder_logger=Logger(
            identifier="PathFinder",
            follow_logger_manager_rules=True,
        ),
        movement_resolution=1,
        arena=self.arena,
    )
    rolling_basis = RollingBasisDummy(
        logger=Logger(
            identifier="RollingBasis",
            follow_logger_manager_rules=True,
        )
    )

    # ---Loop--- #
    movement_manager.arena = self.arena

    if self.go_to_params != movement_manager.params:
        movement_manager.go_to(params=self.go_to_params)
        movement_manager.logger.info("New GoToParams received")

    cmd: RollingBasisCommand = movement_manager.handle_go_to()
    if cmd is not None:
        self.theorical_ally_position.point = cmd.position
        rolling_basis.set_speed_and_position(*cmd.get_command())

        self.rolling_basis_odometrie = rolling_basis.odometrie
        self.add_attributes_to_synchronize("rolling_basis", "theorical_ally_position")

        movement_manager.logger.info(f"RollingBasisCommand: {cmd.get_command()}")
