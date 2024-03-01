from config_loader import CONFIG

# Import from common
from logger import Logger, LogLevels
from geometry import OrientedPoint
from arena import MarsArena
from WS_comms import WSclient, WSclientRouteManager, WSender, WSreceiver, WSmsg

# Import from local path
from sensors import Lidar
from controllers import RollingBasis

import asyncio


async def lidar_brain():
    while True:
        try:
            scan = lidar_obj.scan_to_absolute_cartesian(
                robot_pos=OrientedPoint(
                    robot.odometrie.x, robot.odometrie.y, robot.odometrie.theta
                )
            )
            deserialized_scan = [[s.x, s.y] for s in scan]
            await lidar.sender.send(WSmsg(msg="lidar_scan", data=deserialized_scan))
        except Exception as e:
            print(f"Lidar error : {e}")
        await asyncio.sleep(0.1)


async def odometer_brain():
    while True:
        await odometer.sender.send(
            await odometer.get_ws(),
            WSmsg(
                msg="odometer",
                data=[robot.odometrie.x, robot.odometrie.y, robot.odometrie.theta],
            ),
        )
        await asyncio.sleep(1)


if __name__ == "__main__":
    # Logger
    logger = Logger(
        identifier="robot1",
        dec_level=LogLevels.INFO,
        log_level=LogLevels.DEBUG,
    )
    
    # Arene 
    arena = MarsArena(1)
    
    # Robot
    robot = RollingBasis()
    lidar_obj = Lidar()

    # WS connection
    ws_client = WSclient(CONFIG.WS_SERVER_IP, CONFIG.WS_PORT)

    # Lidar
    lidar = WSclientRouteManager(WSreceiver(), WSender(CONFIG.WS_SENDER_NAME))

    # Log
    log = WSclientRouteManager(WSreceiver(), WSender(CONFIG.WS_SENDER_NAME))

    # Odometer
    odometer = WSclientRouteManager(WSreceiver(), WSender(CONFIG.WS_SENDER_NAME))

    # Bind routes
    ws_client.add_route_handler(CONFIG.WS_LIDAR_ROUTE, lidar)
    ws_client.add_route_handler(CONFIG.WS_LOG_ROUTE, log)
    ws_client.add_route_handler(CONFIG.WS_ODOMETER_ROUTE, odometer)

    # Add background tasks
    ws_client.add_background_task(lidar_brain)
    ws_client.add_background_task(odometer_brain)

    ws_client.run()
