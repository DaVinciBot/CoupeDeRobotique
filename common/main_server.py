from WS.ws_server.ws_server import WServer
from WS.ws_server.ws_server_route import WServerRouteManager
from WS.ws_receiver import WSreceiver
from WS.ws_sender import WSender

import asyncio
from WS.ws_message import WSmsg


async def lidar_brain():
    while True:
        msg = await lidar.receiver.get()
        print(f"#--> Message: {msg}")
        client = lidar.get_client("robot1")
        if client is not None:
            await lidar.sender.send(
                client,
                WSmsg(sender="server", data="Hello from server !")
            )
        await asyncio.sleep(1)


if __name__ == "__main__":
    ws_server = WServer("0.0.0.0", 8080)

    # Lidar route
    lidar = WServerRouteManager(
        WSreceiver(use_queue=True),
        WSender("server")
    )

    # Bind routes
    ws_server.add_route_handler("/lidar", lidar)

    # Add background tasks
    ws_server.add_background_task(lidar_brain)

    ws_server.run()
