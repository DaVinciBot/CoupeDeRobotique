import aiohttp
import asyncio

from WS_comms.client.client_route import WSclientRouteManager
from logger import Logger, LogLevels


class WSclient:
    """
    This class is a client that can connect to a websocket server.
    * This client can connect to multiple routes.
    * It can also run background tasks in parallel with route listening.
    * It can send messages to the server.
    * It can receive messages from the server.
    """

    def __init__(self, host: str, port: int, logger: Logger) -> None:
        self.__host = host
        self.__port = port

        self.logger = logger

        self.tasks = []

    def __get_url(self, route: str) -> str:
        return f"ws://{self.__host}:{self.__port}{route}"

    async def __run_tasks(self) -> None:
        await asyncio.gather(*self.tasks)

    async def __route_handler_routine(self, route, handler):
        """
        This function is a coroutine that connects to a websocket server and binds a handler to it.
        It handle connection errors and try to reconnect to the server.
        :param url:
        :param handler:
        :return:
        """
        self.logger.log(
            f"WSclient [{route}] started, route url: [{self.__get_url(route)}]",
            LogLevels.INFO,
        )
        while True:
            try:
                self.logger.log(
                    f"WSclient [{route}] try to connect server...",
                    LogLevels.INFO,
                )
                async with aiohttp.ClientSession() as session:
                    async with session.ws_connect(
                        f"{self.__get_url(route)}?sender={handler.sender.name}"
                    ) as ws:
                        self.logger.log(
                            f"WSclient [{route}] connected !",
                            LogLevels.INFO,
                        )
                        handler.set_ws(ws)
                        await handler.routine()
            except Exception as error:
                self.logger.log(
                    f"WSclient [{route}] error: ({error}), try to reconnect...",
                    LogLevels.ERROR,
                )

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
        # Add the new routine to the client tasks list with its associated url
        self.tasks.append(self.__route_handler_routine(route, route_manager))

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
