from aiohttp import web
import asyncio

from WS_comms.server.server_route import WServerRouteManager


class WServer:
    """
    This class is websocket server. It is used to handle multiple routes.
    * This server can handle multiple routes.
    * It can handle multiple connections on the same route.
    * It can send messages to the clients.
    * It can receive messages from the clients.
    * It can  run background tasks in parallel with route listening.
    """

    def __init__(self, host: str, port: int) -> None:
        self.__host = host
        self.__port = port

        self.app = web.Application(debug=True)

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
        self.app.router.add_get(route, route_manager.routine)

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
            app[name] = asyncio.create_task(task(*args, **kwargs))

        self.app.on_startup.append(background_task)

    def run(self) -> None:
        web.run_app(self.app, host=self.__host, port=self.__port)
