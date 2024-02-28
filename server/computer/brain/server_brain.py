import asyncio
from logger import Logger, LogLevels
from WS_comms import WSmsg, WServerRouteManager


async def server_brain(
    logger: Logger,
    lidar: WServerRouteManager,
    odometer: WServerRouteManager,
    cmd: WServerRouteManager,
):
    while True:
        try:
            logger.log("Server Brain is working", LogLevels.INFO)

            # Get the message from toutes
            lidar_state = await lidar.receiver.get()
            odometer_state = await odometer.receiver.get()

            # Log states
            logger.log(f"Lidar state: {lidar_state}", LogLevels.INFO)
            logger.log(f"Odometer state: {odometer_state}", LogLevels.INFO)

            # Send message to Robot1
            robot1 = cmd.get_client("robot1")
            if robot1 is not None:
                await cmd.sender.send(
                    WSmsg(
                        msg="test_cmd",
                        data="coucou",
                    ),
                    clients=robot1,
                )

            print("Server Brain is working")
        except Exception as e:
            logger.log(f"Server Brain error: {e}", LogLevels.ERROR)
            print("Server Brain error: ", e)

        await asyncio.sleep(1)
