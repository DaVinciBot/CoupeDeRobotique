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


async def handle_command(com):
    # connect to /cmd endpoint and listen for commands
    async with websockets.connect(uri + "/cmd") as websocket:
        data = await websocket.recv()
        if data == "foward":
            com.Go_To([1, 0, 0])
        elif data == "backward":
            com.Go_To([1, 0, 0], direction=True)
        elif data == "left":
            com.Go_To([0, 1, 0])
        elif data == "right":
            com.Go_To([0, 1, 0], direction=True)
        elif data == "stop":
            com.Go_To([0, 0, 0])
