import asyncio
import json
import os
import websockets



CONNECTIONS_LIDAR = set()


async def middleware(websocket):
    CONNECTIONS_LIDAR.add(websocket)
    try:
        await handle_lidar_ws(websocket)
        await websocket.wait_closed()
    finally:
        CONNECTIONS_LIDAR.remove(websocket)


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


async def handle_lidar_ws(websocket):
    async for msg in websocket:
        if msg.split(":")[0] == "get":
            data = get_lidar_data()
            await websocket.send("current:" + json.dumps(data))
        elif msg.split(":")[0] == "set":
            data = list(
                map(
                    float,
                    msg.split(":")[1].replace("[", "").replace("]", "").split(","),
                )
            )
            set_lidar_data(data)
            # then notify all clients
            for client in CONNECTIONS_LIDAR:
                await client.send("new:" + json.dumps(data))
            await websocket.send("ok")
        else:
            await websocket.send("error")


async def main():
    async with websockets.serve(middleware, "0.0.0.0", 3000):
        await asyncio.Future()  # serve forever


def run():
    asyncio.run(main())


if __name__ == "__main__":
    run()
