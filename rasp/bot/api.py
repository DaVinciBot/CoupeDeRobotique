import websockets

IP = "rc.local"
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


async def get_last_command():
    # connect to /cmd endpoint and listen for commands
    # check if message is received
    # if yes, return it

    async with websockets.connect(uri + "/cmd") as websocket:
        await websocket.send("get$=$")
        resp = await websocket.recv()
        if resp == "None" or resp == "error" or resp == "":
            return None
        else:
            cmd = resp[:4]
            args = None
            try:
                args = list(map(float,resp[4:].replace("[", "").replace("]", "").split(",")))
            except IndexError:
                pass
            return cmd, args


async def send_action_finished():
    async with websockets.connect(uri + "/cmd") as websocket:
        await websocket.send("finished$=$")