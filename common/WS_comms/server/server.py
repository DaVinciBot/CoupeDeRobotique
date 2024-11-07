from aiohttp import web
import asyncio
import signal
import time

from WS_comms.server.server_route import WServerRouteManager
from logger import Logger, LogLevels


class WServer:
    """
    This class is websocket server. It is used to handle multiple routes.
    * This server can handle multiple routes.
    * It can handle multiple connections on the same route.
    * It can send messages to the clients.
    * It can receive messages from the clients.
    * It can  run background tasks in parallel with route listening.
    """

    def __init__(
        self,
        logger: Logger,
        host: str,
        port: int,
        ping_pong_clients_interval: int = None,
    ) -> None:
        self.__logger = logger

        self.__host = host
        self.__port = port

        # self.__ping_pong_clients_interval = ping_pong_clients_interval

        self._app = web.Application(debug=True)

        # Keep access on the route manager
        self.__route_managers = {}
        # Keep access on the background tasks
        self.__background_tasks = set()

    # async def __ping_pong_clients_task(self, interval: int):
    #     while True:
    #         for route, manager in self.__route_managers.items():
    #             for client_name, client_ws_connection in manager.clients.items():
    #                 try:
    #                     await client_ws_connection.ping()
    #                     continue
    #                 except asyncio.TimeoutError:
    #                     self.__logger.log(
    #                         f"Pinging timeout [{client_name}] on route [{route}]. "
    #                         f"The client have been suddenly disconnected.",
    #                         LogLevels.WARNING,
    #                     )
    #                 except websockets.exceptions.ConnectionClosed:
    #                     self.__logger.log(
    #                         f"Connection closed [{client_name}] on route [{route}]. "
    #                         f"The client have been suddenly disconnected.",
    #                         LogLevels.WARNING,
    #                     )
    #                 except Exception as error:
    #                     self.__logger.log(
    #                         f"Error while pinging client [{client_name}] on route [{route}]. "
    #                         f"The client have been suddenly disconnected ({error})",
    #                         LogLevels.WARNING,
    #                     )
    #                 del manager.clients[client_name]
    #         await asyncio.sleep(interval)

    def add_route_handler(self, route: str, route_manager: WServerRouteManager) -> None:
        """
        Add a new route to the server.
            - route is the path of url to bind to the handler.
            - route_manager is an object that manage the connection with the client(s). It manages the client(s)
            list and allows to send and receive messages.
        :param route:
        :param route_manager:
        :return:
        """
        self.__logger.log(
            f"New route handler added [{route}], route url: [ws://{self.__host}:{self.__port}{route}]",
            LogLevels.DEBUG,
        )
        self.__route_managers[route] = route_manager
        self._app.router.add_get(route, route_manager.routine)

    def add_background_task(
        self, task: callable, *args, name: str = "", **kwargs
    ) -> None:
        """
        Add a new background task to the server. It is useful to execute task in parallel with the server.
        * The task have to be a coroutine (async function).
        * To create the task we add a key in the app dictionary with the name of the task.
        * The task will be created when the server will start.
        * Format: add_background_task(func, (optional) func_params, (optional) name)
        :param task:
        :param args:
        :param name:
        :param kwargs:
        :return:
        """
        name = task.__name__ if name == "" else name

        async def background_task(app):
            task_instance = asyncio.create_task(task(*args, **kwargs))
            app[name] = task_instance
            self.__background_tasks.add(task_instance)

        self.__logger.log(
            f"New background task added [{name}]",
            LogLevels.DEBUG,
        )
        self._app.on_startup.append(background_task)

    async def stop_server(self):
        """
        Stop the server and all the background tasks.
        :return:
        """
        self.__logger.log("Received exit signal...", LogLevels.WARNING)

        # Close all the ws connections for all the routes
        self.__logger.log("Closing all connections...", LogLevels.INFO)
        for route, manager in self.__route_managers.items():
            self.__logger.log(
                f"Closing all connections for [{route}] route.", LogLevels.DEBUG
            )
            await manager.close_all_connections()

        # End all the background tasks
        tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)

        # Stop asyncio loop
        asyncio.get_event_loop().close()
        self._app._loop.close()

    def add_background_task(
        self, task: callable, *args, name: str = "", **kwargs
    ) -> None:
        """
        Add a new background task to the server. It is useful to execute task in parallel with the server.
        * The task have to be a coroutine (async function).
        * To create the task we add a key in the app dictionary with the name of the task.
        * The task will be created when the server will start.
        * Format: add_background_task(func, (optional) func_params, (optional) name)
        :param task:
        :param args:
        :param name:
        :param kwargs:
        :return:
        """
        name = task.__name__ if name == "" else name

        async def background_task(app):
            task_instance = asyncio.create_task(task(*args, **kwargs))
            app[name] = task_instance
            self.__background_tasks.add(task_instance)

        self.__logger.log(
            f"New background task added [{name}]",
            LogLevels.DEBUG,
        )
        self._app.on_startup.append(background_task)

    def run(self) -> None:
        loop = asyncio.get_event_loop()

        def handle_exit():
            self.__logger.log("WServer stopped by user request.", LogLevels.INFO)
            asyncio.create_task(self.stop_server())
            loop.close()

        loop.add_signal_handler(signal.SIGINT, handle_exit)

        try:
            self.__logger.log(
                f"WServer started, url: [ws://{self.__host}:{self.__port}]",
                LogLevels.INFO,
            )
            # Ping pong mode does not work for now, if you want to use it,
            # you have to remove the non-unique client identifier or adapt
            # current function to handle multiple clients with the same name
            # if self.__ping_pong_clients_interval is not None:
            #     self.add_background_task(
            #         self.__ping_pong_clients_task,
            #         interval=self.__ping_pong_clients_interval,
            #     )
            #     self.__logger.log(
            #         f"Ping pong mode activated, interval: [{self.__ping_pong_clients_interval}]",
            #         LogLevels.DEBUG,
            #     )
            web.run_app(self._app, host=self.__host, port=self.__port)
        except Exception as error:
            self.__logger.log(
                f"WServer error: ({error}), try to restart...", LogLevels.ERROR
            )
            time.sleep(5)
        finally:
            loop.close()
