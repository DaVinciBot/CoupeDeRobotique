import aiohttp
import asyncio

from WS_comms.client.client_route import WSclientRouteManager


class WSclient:
    """
    This class is a client that can connect to a websocket server.
    * This client can connect to multiple routes.
    * It can also run background tasks in parallel with route listening.
    * It can send messages to the server.
    * It can receive messages from the server.
    """

    def __init__(self, host: str, port: int) -> None:
        self.__host = host
        self.__port = port

        self.tasks = []

    def __get_url(self, route: str) -> str:
        return f"ws://{self.__host}:{self.__port}{route}"

    async def __run_tasks(self) -> None:
        await asyncio.gather(*self.tasks)

    def add_route_handler(
        self, route: str, route_manager: WSclientRouteManager
    ) -> None:
        """
        Add a new route to the client.
            - route is the path of url to bind to the handler.
            - route_manager is an object that manage the connection with the server. It establishes
            the connection with the server and allows to send and receive messages.
        :param route:
        :param route_manager:
        :return:
        """

        # Create a new routine to handle the new route
        async def routine(url, handler):
            async with aiohttp.ClientSession() as session:
                async with session.ws_connect(
                    f"{url}?sender={handler.sender.name}"
                ) as ws:
                    handler.set_ws(ws)
                    await handler.routine()

        # Add the new routine to the client tasks list with its associated url
        self.tasks.append(routine(self.__get_url(route), route_manager))

    def add_background_task(self, task: callable, *args, **kwargs) -> None:
        """
        Add a new background task to the client. It is useful to execute task in parallel with the client.
        * The task have to be a coroutine (async function).
        * The task will be created when the client will start.
        :param task:
        :return:
        """
        self.tasks.append(task(*args, **kwargs))

    def run(self) -> None:
        asyncio.run(self.__run_tasks())
