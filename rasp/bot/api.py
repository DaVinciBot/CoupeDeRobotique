import websockets

IP = "10.3.141.218"  # Replace by the Remote Compute IP
PORT = 3000
uri = f"ws://{IP}:{PORT}"


async def update_lidar(data: list[float]):
    async with websockets.connect(uri + "/lidar") as websocket:
        data = list(map(str, data))
        data = "[" + ",".join(data) + "]"
        await websocket.send("set$=$" + data)


async def update_log(data: str):
    async with websockets.connect(uri + "/log") as websocket:
        await websocket.send("update$=$[" + data + "]")


async def get_last_command() -> list[str] or None:
    # connect to /cmd endpoint and listen for commands
    # check if message is received
    # if yes, return it

    async with websockets.connect(uri + "/cmd") as websocket:
        await websocket.send("get$=$")
        resp = await websocket.recv()
        if resp == "None" or resp == "error" or resp == "":
            return None
        else:
            cmd = resp.split("$=$")[0]
            args = list(map(float,resp.split("$=$")[1].replace("[", "").replace("]", "").split(",")))
            return cmd, args
