import aiohttp

from WS_comms.message import WSmsg

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
        if not isinstance(clients, list):
            self.__route_manager_clients = [clients]
        else:
            self.__route_manager_clients = clients

    async def get_clients(self, wait_clients: bool = False) -> list:
        while len(self.__route_manager_clients) == 0 and wait_clients:
            await asyncio.sleep(0.5)
            # print("No clients ...")
        return self.__route_manager_clients

    async def send(self, msg: WSmsg, clients=None, wait_client: bool = False) -> bool:
        """
        Send a message to one or multiple clients.
        :param msg:
        :param clients:
        :param wait_client:
        :return:
        """
        # Add the source value to the message
        msg.sender = self.name

        # By default send to attributes clients
        if clients is None:
            clients = await self.get_clients(wait_client)

        if clients is None:
            # print("Error, no clients found.")
            return False

        if type(clients) is not list:
            clients = [clients]

        for client in clients:
            try:
                await client.send_str(msg.prepare())
                return True
            except Exception as error:
                print(f"Error during sending message: {error}")
                return False
