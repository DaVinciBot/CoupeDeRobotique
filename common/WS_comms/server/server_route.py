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

        # Clients set format:
        # {
        #   "client_name": [client_ws_connection, ...]
        # }
        self.clients = {}

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
        # Use get URL value instead
        client_name = request.query.get("sender")

        # Check source validity
        if client_name is None:
            raise ValueError(
                "New client does not have a sender value in url parameter. CONNECTION REFUSED."
            )
        # Check if the client name already exists
        if self.clients.get(client_name) is None:
            self.clients[client_name] = []

        # Add the new client associated to the source value
        self.clients[client_name].append(client)

        # Old version with unique name per client
        # if self.clients.get(client_name) is not None:
        #    raise ValueError(
        #        f"Client with name [{client_name}] already exists. CONNECTION REFUSED."
        #    )
        return client_name

    def get_client(self, name: str) -> list[aiohttp.web_ws.WebSocketResponse]:
        """
        Get a client by its source value (its name).
        :param name:
        :return: list of clients associated to the source name
        """
        # if self.clients.get(name) is None:
        #    raise ValueError(f"Client with source [{name}] does not exist.")
        return self.clients.get(name, [])

    def get_all_clients(self):
        # Concatenate all clients in a list
        return [item for sublist in list(self.clients.values()) for item in sublist]

    async def close_all_connections(self):
        """
        Close all active WebSocket connections.
        """
        # Loop through all clients and close each WebSocket connection
        for client_name, client in self.get_all_clients():
            if not client.closed:
                await client.close()
            print(f"Closed connection for {client_name}")
        self.clients.clear()

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
            self.sender.update_clients(self.get_all_clients())
            print(f"Client disconnected [{client_name}]")

        return client
