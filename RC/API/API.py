import asyncio
import json
import os
import websockets
import datetime


def get_lidar_data() -> list[float]:
    if "lidar.json" not in os.listdir("."):
        create_lidar_data()
    # read file lidar.json
    with open("lidar.json") as f:
        data = json.load(f)["data"]
    return data


def set_lidar_data(data: list[float]):
    # write file lidar.json
    with open("lidar.json", "w") as f:
        json.dump({"data": data}, f)


def create_lidar_data():
    # create file lidar.json
    with open("lidar.json", "w") as f:
        json.dump({"data": [5.0 for i in range(810)]}, f)


def get_log_data() -> list[str]:
    date = datetime.datetime.now()
    file = f"{date.strftime('%Y-%m-%d')}.log"
    if file not in os.listdir("logs"):
        set_log_data(["test"])
    with open("logs/" + file) as f:
        data = f.readlines()
        data = [line.replace("\n", "") for line in data]
    return data


def set_log_data(data: list[str]):
    if "logs" not in os.listdir("."):
        os.mkdir("logs")
    date = datetime.datetime.now()
    file = f"{date.strftime('%Y-%m-%d')}.log"
    with open("logs/" + file, "w+") as f:
        # add \n to each line
        data = [line + "\n" for line in data]
        f.writelines(data)


def update_log_data(data: list[str]):
    if "logs" not in os.listdir("."):
        os.mkdir("logs")
    date = datetime.datetime.now()
    file = f"{date.strftime('%Y-%m-%d')}.log"
    with open("logs/" + file, "a") as f:
        # add \n to each line
        data = [line + "\n" for line in data]
        f.writelines(data)


async def handle_lidar_ws(
    websocket: websockets.WebSocketServerProtocol, CONNECTIONS_LIDAR
):
    """
    Handle websocket connection for /lidar endpoint, with get/set methods, and subscribe to new data

    :param websocket: the websocket connection
    :type websocket: websockets.WebSocketServerProtocol
    """
    async for msg in websocket:
        if msg.split("$=$")[0] == "get":
            data = get_lidar_data()
            await websocket.send("current$=$" + json.dumps(data))
        elif msg.split("$=$")[0] == "set":
            data = list(
                map(
                    float,
                    msg.split("$=$")[1].replace("[", "").replace("]", "").split(","),
                )
            )
            set_lidar_data(data)
            # then notify all clients
            for client in CONNECTIONS_LIDAR:
                await client.send("new$=$" + json.dumps(data))
            await websocket.send("ok")
        else:
            await websocket.send("error")


async def handle_log_ws(websocket: websockets.WebSocketServerProtocol, CONNECTIONS_LOG):
    """
    Handle websocket connection for /log endpoint, with get/set/update methods, and subscribe to new data

    :param websocket: _description_
    :type websocket: _type_
    """
    async for msg in websocket:
        if msg.split("$=$")[0] == "get":
            data = get_log_data()
            await websocket.send("current$=$" + json.dumps(data))
        elif msg.split("$=$")[0] == "set":
            data = list(
                map(
                    str,
                    msg.split("$=$")[1].replace("[", "").replace("]", "").split(","),
                )
            )
            set_log_data(data)
            # then notify all clients
            for client in CONNECTIONS_LOG:
                await client.send("new$=$" + json.dumps(data))
            await websocket.send("ok")
        elif msg.split(":")[0] == "update":
            data = list(
                map(
                    str,
                    msg.split("$=$")[1].replace("[", "").replace("]", "").split(","),
                )
            )
            update_log_data(data)
            # then notify all clients
            for client in CONNECTIONS_LOG:
                await client.send("new$=$" + json.dumps(data))
            await websocket.send("ok")
        else:
            await websocket.send("error")


class API:
    """
    Wrapper for websockets server, take a dict of endpoints, with a set of connections and a handler for each endpoint
    """

    def __init__(self, SERVER, ip: str = "0.0.0.0", port: int = 3000) -> None:
        self.ip = ip
        self.port = port
        self.SERVER = SERVER

    async def __server(self):
        print("Starting server...")
        async with websockets.serve(self.middleware, self.ip, self.port):
            await asyncio.Future()  # serve forever

    def run(self):
        asyncio.run(self.__server())

    async def middleware(self, websocket: websockets.WebSocketServerProtocol):
        # use SERVER for set of connections and handler
        for key in self.SERVER:
            if websocket.path == f"/{key}":
                self.SERVER[key]["connections"].add(websocket)
                try:
                    await self.SERVER[key]["handler"](
                        websocket, self.SERVER[key]["connections"]
                    )
                    await websocket.wait_closed()
                finally:
                    self.SERVER[key]["connections"].remove(websocket)
