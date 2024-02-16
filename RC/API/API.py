import asyncio
import json
import os
import websockets
import datetime
import socket

"""
Format of communication between server and robot through websockets, in JSON:
{
    "sender":"robot/server/...",
    "action":"get/set/...",
    "data":... (optional)
}
"""

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


def load_state_from_file():
    try:
        with open("state.json", "r") as file:
            state = json.load(file)
    except FileNotFoundError:
        state = {
            "pins": {},
            "position": {},
            "current_action": "",
            "action_list": [],
        }
        # charge default value if the document does not exist
    return state


# retreive information
def get_state(key=None):
    current_state = load_state_from_file()
    if key is None or key == "all" or key == "":
        return current_state
    if key in current_state:
        return {key: current_state[key]}
    return None


# define the state for a specific key
def set_state(key, value):
    current_state = load_state_from_file()
    if key in current_state:
        current_state[key] = value
        with open("state.json", "w") as file:
            json.dump(current_state, file)
        return f"OK"
    return f"ERROR: key '{key}' not found"


# update with new infos
def update_state(data):
    current_state = load_state_from_file()
    current_state.update(data)


async def handle_state_ws(websocket, CONNECTIONS_STATE):

    # sending the current state of the client on connection
    state_message = json.dumps(load_state_from_file())
    await websocket.send(state_message)

    async for message in websocket:
        try:
            data = json.loads(message)
        except json.JSONDecodeError:
            await websocket.send("error: message non valide")
            continue
        operation = data.get("operation")
        key = data.get("key")

        if operation == "get":
            # get a state of a specific key
            response = get_state(key)
            await websocket.send(json.dumps(response))
        elif operation == "set" and key:
            # modify state of a specific key
            new_value = data.get("value")
            response = set_state(key, new_value)
            await websocket.send(json.dumps(response))
        elif operation == "update" and key:
            # update with new infos
            new_data = data.get("data")
            update_state(new_data)
        else:
            await websocket.send("error : operation non valide")


async def handle_lidar_ws(
    websocket: websockets.WebSocketServerProtocol, CONNECTIONS_LIDAR
):
    """
    Handle websocket connection for /lidar endpoint, with get/set methods, and subscribe to new data

    :param websocket: the websocket connection
    :type websocket: websockets.WebSocketServerProtocol
    """
    async for msg in websocket:
        content = json.loads(msg)

        if content["action"] == "get":
            data = get_lidar_data()

            await websocket.send_json({
                "sender":"server",
                "action":"response",
                "data":data
            })

        elif content["action"] == "set":
            data = content["data"]
            set_lidar_data(data)

        # then notify all clients
            for client in CONNECTIONS_LIDAR:
                await client.send_json({
                    "sender":"server",
                    "action":"new",
                    "data":data
                })
            await websocket.send_json({
                    "sender":"server",
                    "action":"ok"
                })
        else:
            await websocket.send_json({
                    "sender":"server",
                    "action":"error"
                })

        # if msg.split("$=$")[0] == "get":
        #     data = get_lidar_data()
        #     await websocket.send("current$=$" + json.dumps(data))
        # elif msg.split("$=$")[0] == "set":
        #     data = list(
        #         map(
        #             float,
        #             msg.split("$=$")[1].replace("[", "").replace("]", "").split(","),
        #         )
        #     )
        #     set_lidar_data(data)
        #     # then notify all clients
        #     for client in CONNECTIONS_LIDAR:
        #         await client.send("new$=$" + json.dumps(data))
        #     await websocket.send("ok")
        # else:
        #     await websocket.send("error")


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
        elif msg.split("$=$")[0] == "update":
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


async def handle_pos_ws(
    websocket: websockets.WebSocketServerProtocol, CONNECTIONS_POS: set
):
    """
    Redirect all messages to all clients

    :param websocket: the websocket connection
    :type websocket: websockets.WebSocketServerProtocol
    :param CONNECTIONS_CMD: set of connections
    :type CONNECTIONS_CMD: set
    """
    async for msg in websocket:
        # save message, and send it when get$=$ is received
        if msg.split("$=$")[0] == "set":
            data = msg.split("$=$")[1]
            with open("position.txt", "w") as f:
                f.write(data)
            await websocket.send("ok")
            for client in CONNECTIONS_POS:
                await client.send("new$=$" + str(data))
        elif msg.split("$=$")[0] == "get":
            with open("position.txt") as f:
                data = f.read()
            await websocket.send("current$=$" + str(data))
        elif msg.split("$=$")[0] == "finished":
            with open("last_command.txt", "w") as f:
                f.write("None")
            await websocket.send("ok")
        else:
            await websocket.send("error")


async def handle_cmd_ws(
    websocket: websockets.WebSocketServerProtocol, CONNECTIONS_CMD: set
):
    """
    Redirect all messages to all clients

    :param websocket: the websocket connection
    :type websocket: websockets.WebSocketServerProtocol
    :param CONNECTIONS_CMD: set of connections
    :type CONNECTIONS_CMD: set
    """
    async for msg in websocket:
        # save message, and send it when get$=$ is received
        if msg.split("$=$")[0] == "set":
            data = msg.split("$=$")[1]
            with open("last_command.txt", "w") as f:
                f.write(data)
            await websocket.send("ok")
        elif msg.split("$=$")[0] == "get":
            with open("last_command.txt") as f:
                data = f.read()
            await websocket.send(data)
        elif msg.split("$=$")[0] == "finished":
            with open("last_command.txt", "w") as f:
                f.write("None")
            await websocket.send("ok")
        else:
            await websocket.send("error")


COLORS = {
    "GREEN": "\x1b[6;30;42m",
    "RED": "\x1b[6;30;41m",
    "YELLOW": "\x1b[6;30;43m",
    "BLUE": "\x1b[6;30;44m",
    "GRAY": "\x1b[90m",
    "WHITE": "\x1b[97m",
    "UNDERLINE": "\x1b[4m",
    "END_UNDERLINE": "\x1b[24m",
    "END": "\x1b[0m",
}


class API:
    """
    Wrapper for websockets server, take a dict of endpoints, with a set of connections and a handler for each endpoint
    """

    def __init__(self, SERVER, ip: str = "0.0.0.0", port: int = 3000) -> None:
        self.ip = ip
        self.port = port
        self.SERVER = SERVER

        self.__local_ip = socket.gethostbyname(socket.gethostname())

    async def __server(self):
        async with websockets.serve(self.middleware, self.ip, self.port):
            print(
                f"{COLORS['GREEN']} Server started on port {self.port} and interface {self.ip} {COLORS['END']}\n{COLORS['GRAY']}→  access from local computer: {COLORS['UNDERLINE'] + COLORS['WHITE']}ws://localhost:{self.port}/<route>{COLORS['END_UNDERLINE']+COLORS['GRAY']}\n→  from other computer: {COLORS['UNDERLINE'] + COLORS['WHITE']}ws://{self.__local_ip}:{self.port}/<route>{COLORS['END_UNDERLINE']+COLORS['GRAY']} {COLORS['END']}\n\nLog:"
            )
            await asyncio.Future()  # serve forever

    def run(self):
        try:
            asyncio.run(self.__server())
        except KeyboardInterrupt:
            print(f"{COLORS['YELLOW']} Server stopped {COLORS['END']}")

    async def middleware(self, websocket: websockets.WebSocketServerProtocol):
        # use SERVER for set of connections and handler
        print(
            f"{COLORS['BLUE']} New connection on route {COLORS['UNDERLINE']+websocket.path} {COLORS['END']}"
        )
        for key in self.SERVER:
            if websocket.path == f"/{key}":
                self.SERVER[key]["connections"].add(websocket)
                try:
                    await self.SERVER[key]["handler"](
                        websocket, self.SERVER[key]["connections"]
                    )
                    await websocket.wait_closed()
                finally:
                    print(
                        f"{COLORS['BLUE']} Connection closed on route {COLORS['UNDERLINE']+websocket.path} {COLORS['END']}"
                    )
                    self.SERVER[key]["connections"].remove(websocket)
