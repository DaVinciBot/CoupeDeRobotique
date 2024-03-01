# Import from common
from logger import Logger, LogLevels
from geometry import OrientedPoint, Point
from arena import MarsArena
from WS_comms import WSmsg, WServerRouteManager
from brain import Brain

# Import from local path
# ..

import asyncio


class ServerBrain(Brain):
    def __init__(
        self,
        logger: Logger,
        arene: MarsArena,
        lidar_ws: WServerRouteManager,
        odometer_ws: WServerRouteManager,
        cmd_ws: WServerRouteManager
    ) -> None:
        super().__init__(logger)
            
        self.arene = arene
        self.lidar_ws = lidar_ws
        self.odometer_ws = odometer_ws
        self.cmd_ws = cmd_ws
        
    async def logical(self):
        self.logger.log("Server Brain is working", LogLevels.INFO)

        # Get the message from toutes
        lidar_state = await self.lidar.receiver.get()
        odometer_state = await self.odometer.receiver.get()

        # Log states
        self.logger.log(f"Lidar state: {lidar_state}", LogLevels.INFO)
        self.logger.log(f"Odometer state: {odometer_state}", LogLevels.INFO)

        # Send message to Robot1
        robot1 = self.cmd.get_client("robot1")
        if robot1 is not None:
            await self.cmd.sender.send(
                WSmsg(
                    msg="test_cmd",
                    data="coucou",
                ),
                clients=robot1,
            )

        await asyncio.sleep(1)
