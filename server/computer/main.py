from config_loader import CONFIG

# Import from common
from WS_comms import WServer, WServerRouteManager, WSender, WSreceiver, WSmsg
from logger import Logger, LogLevels

# Import from local path
from brain.server_brain import server_brain

import asyncio


# async def lidar_brain(lidar: WServerRouteManager, logger: Logger):
#     while True:
#         msg = await lidar.receiver.get()
#         if msg != WSmsg():
#             logger.log(
#                 f"Message lidar: {msg.msg}, {msg.sender}, {len(msg.data)}",
#                 LogLevels.INFO,
#             )
#             print(
#                 f"#--> Message lidar: {msg.msg}, {msg.sender}, {len(msg.data)}, queue: {lidar.receiver.get_queue_size()}"
#             )
#         else:
#             print(f"#--> Message lidar: {msg}")

#         await asyncio.sleep(5)


if __name__ == "__main__":
    logger = Logger(
        identifier="computer",
        dec_level=LogLevels.INFO,
        log_level=LogLevels.DEBUG,
    )
    ws_server = WServer(CONFIG.WS_HOSTNAME, CONFIG.WS_PORT)

    # Lidar
    lidar = WServerRouteManager(
        WSreceiver(keep_memory=True, use_queue=True), WSender(CONFIG.WS_SENDER_NAME)
    )

    # Log
    log = WServerRouteManager(
        WSreceiver(use_queue=True), WSender(CONFIG.WS_SENDER_NAME)
    )

    # Odometer
    odometer = WServerRouteManager(
        WSreceiver(keep_memory=True), WSender(CONFIG.WS_SENDER_NAME)
    )

    # Cmd
    cmd = WServerRouteManager(WSreceiver(), WSender(CONFIG.WS_SENDER_NAME))

    # Bind routes
    ws_server.add_route_handler(CONFIG.WS_LIDAR_ROUTE, lidar)
    ws_server.add_route_handler(CONFIG.WS_LOG_ROUTE, log)
    ws_server.add_route_handler(CONFIG.WS_ODOMETER_ROUTE, odometer)
    ws_server.add_route_handler("/cmd", cmd)

    # Add background tasks, in format ws_server.add_background_task(func, func_params)
    ws_server.add_background_task(server_brain, logger, lidar, odometer, cmd)

    ws_server.run()
