import asyncio
import websockets

async def update_lidar(data: list[float]):
    IP = "10.3.141.218"
    uri = f"ws://{IP}:3000"
    async with websockets.connect(uri) as websocket:
        await websocket.send("set:"+data)

