from rolling_basis_handler import RollingBasisHandler
from path_finding import PathFinder
from arena import ShowArena
from logger import Logger, LogLevels
from arena import BaseArenaZone
from geometry import OrientedPoint


class MovementManager:
    def __init__(self, arena: ShowArena):
        self.arena = arena

        self.logger = Logger(
            identifier="MovementManager",
            decorator_level=LogLevels.INFO,
            print_log_level=LogLevels.DEBUG,
            file_log_level=LogLevels.DEBUG,
        )
        self.logger_rolling_basis_handler = Logger(
            identifier="Rolling_basisHandler",
            decorator_level=LogLevels.INFO,
            print_log_level=LogLevels.DEBUG,
            file_log_level=LogLevels.DEBUG,
        )

    def goto(self, destination: OrientedPoint):
        rolling_basis_handler = RollingBasisHandler(
            profile=self.arena.speed_profile,
            trajectory=self.arena.get_trajectory(destination),
        )
        rolling_basis_handler.run()
        return rolling_basis_handler
