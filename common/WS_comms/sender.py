import aiohttp

from WS.ws_message import WSmsg

import asyncio

class WSender:
    """
    This class is used to send messages to clients.
    Every sent messages are marked with the source value of the sender (this machine name).
    """

    def __init__(self, name: str) -> None:
        """
        Initialize the sender with its name value.
        This value is used to identify the sender.
        :param name:
        """
        self.name = name

        self.__route_manager_clients = []

    def update_clients(self, clients) -> None:
        if type(clients) is not list:
            self.__route_manager_clients = [clients]
        else:
            self.__route_manager_clients = clients

    async def get_clients(self, wait_clients: bool = False) -> list:
        while len(self.__route_manager_clients) == 0 and not wait_clients:
            await asyncio.sleep(0.5)
        return self.__route_manager_clients


    async def send(self, clients = None, msg: WSmsg, wait_client: bool = False) -> None:
        """
        Send a message to one or multiple clients.
        :param clients:
        :param msg:
        :return:
        """
        # Add the source value to the message
        msg.sender = self.name

        # By default send to attributes clients
        if clients is None:
            clients = await self.get_clients(wait_client)

        if clients is None:
            print("Error, no clients found.")
            return

        if type(clients) is not list:
            clients = [clients]

        for client in clients:
            await client.send_str(msg.prepare())
