import websockets

IP = "10.3.141.218" # Replace by the Remote Compute IP
PORT = 3000
uri = f"ws://{IP}:{PORT}"


async def update_lidar(data: list[float]):
    async with websockets.connect(uri+"/lidar") as websocket:
        data = list(map(str, data))
        data = "[" + ",".join(data) + "]"
        await websocket.send("set:"+data)


async def update_log(data: str):
    async with websockets.connect(uri+"/log") as websocket:
        await websocket.send("update:["+data+"]")



