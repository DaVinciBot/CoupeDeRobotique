import aiohttp
import asyncio

from WS_comms.receiver import WSreceiver
from WS_comms.sender import WSender


class WSclientRouteManager:
    """
    This class is used to manage a route. It is used to manage a route by establishing
    the client-server connection, listening server message, sending message to the server.
    Sending and listening are managed by a receiver and a sender object.
    * Its routine has to be given at the route creation.
    """

    def __init__(self, receiver: WSreceiver, sender: WSender) -> None:
        self.receiver = receiver
        self.sender = sender

        self.__ws = None

    def set_ws(self, ws: aiohttp.ClientWebSocketResponse) -> None:
        self.__ws = ws
        self.sender.update_clients(ws)

    async def get_ws(self, skip_set=False) -> aiohttp.ClientWebSocketResponse or None:
        # Wait until the ws is connected
        while self.__ws is None and not skip_set:
            await asyncio.sleep(0.5)
        return self.__ws

    async def routine(self) -> None:
        """
        Routine to handle a connection on a specific route.
        * It is used to listen to the server messages.
        """
        try:
            async for msg in self.__ws:
                #print("Received message : ", msg)
                await self.receiver.routine(msg)

        except Exception as error:
            print(f"Error during connection handling: {error}")

        finally:
            print("Connection closed")
