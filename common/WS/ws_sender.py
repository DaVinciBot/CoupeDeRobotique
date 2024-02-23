import aiohttp

from WS.ws_message import WSmsg


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

    async def send(self, clients, msg: WSmsg) -> None:
        """
        Send a message to one or multiple clients.
        :param clients:
        :param msg:
        :return:
        """
        # Add the source value to the message
        msg.sender = self.name

        if type(clients) is not list:
            clients = [clients]

        for client in clients:
            await client.send_str(msg.prepare())
