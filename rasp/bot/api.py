import asyncio
import websockets

IP = "10.3.141.218" # Replace by the Remote Compute IP
PORT = 3000
uri = f"ws://{IP}:{PORT}"

def update_lidar(data: list[float]):
    with websockets.connect(uri+"/lidar") as websocket:
        data = list(map(str, data))
        data = "[" + ",".join(data) + "]"
        asyncio.run(websocket.send("set:"+data))


def update_log(data: str):
    with websockets.connect(uri+"/log") as websocket:
        asyncio.run(websocket.send("update:["+data+"]"))



