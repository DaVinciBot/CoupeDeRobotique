from WS.ws_client.ws_client import WSclient
from WS.ws_client.ws_client_route import WSclientRouteManager
from WS.ws_receiver import WSreceiver
from WS.ws_sender import WSender
from WS.ws_message import WSmsg

import asyncio

async def brain():
    while True:
        msg = await lidar.receiver.get()
        print(f"#--> Message: {msg}")
        try:
            await lidar.sender.send(
                await lidar.get_ws(),
                WSmsg(sender="client", data="Hello from client !")
            )
        except Exception as error:
            print(f"Error during sending: {error}")
        await asyncio.sleep(1)


if __name__ == "__main__":
    ws_client = WSclient("localhost", 8080)

    # Lidar route
    lidar = WSclientRouteManager(
        WSreceiver(),
        WSender("robot1")
    )

    ws_client.add_route_handler("/lidar", lidar)
    ws_client.add_background_task(brain)
    ws_client.run()
