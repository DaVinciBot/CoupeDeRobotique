import aiohttp

from WS_comms.receiver import WSreceiver
from WS_comms.sender import WSender


class WServerRouteManager:
    """
    this class is used to manage a route. It is used to handle new connections and to manage the clients list.
    It is also composed by a receiver and a sender, which can be used to manage the messages (send or receive).
    * Its routine has to be given at the route creation.
    """

    def __init__(self, receiver: WSreceiver, sender: WSender) -> None:
        self.receiver = receiver
        self.sender = sender

        self.clients = dict()

    def add_client(
        self,
        request: aiohttp.web_request.Request,
        client: aiohttp.web_ws.WebSocketResponse,
    ) -> str:
        """
        Add a new client in the router handler list.
        :param request:
        :param client:
        :return:
        """
        client_name = request.headers.get("sender")

        # Check source validity
        if client_name is None:
            raise ValueError(
                "New client does not have a source value in the header. CONNECTION REFUSED."
            )
        if self.clients.get(client_name) is not None:
            raise ValueError(
                f"Client with name [{client_name}] already exists. CONNECTION REFUSED."
            )

        # Add the new client associated to the source value
        self.clients[client_name] = client

        return client_name

    def get_client(self, name: str) -> aiohttp.web_ws.WebSocketResponse or None:
        """
        Get a client by its source value (its name).
        :param name:
        :return:
        """
        # if self.clients.get(name) is None:
        #    raise ValueError(f"Client with source [{name}] does not exist.")
        return self.clients.get(name)

    def get_all_clients(self):
        return [val for val in self.clients.values()]

    async def routine(
        self, request: aiohttp.web_request.Request
    ) -> aiohttp.web_ws.WebSocketResponse or None:
        """
        Routine to handle new connections.
        * It supports multiple clients / new connections / disconnections.
        :param request:
        :return:
        """
        client = aiohttp.web.WebSocketResponse()
        await client.prepare(request)

        client_name = self.add_client(request, client)
        print("New client : ", client_name)
        self.sender.update_clients(self.get_all_clients())
        try:
            async for msg in client:
                await self.receiver.routine(msg)

        except Exception as error:
            print(f"Error during connection handling: {error}")

        finally:
            del self.clients[client_name]
            print(f"Client disconnected [{client_name}]")

        return client
