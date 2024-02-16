import asyncio
import websockets

IP = "rc.local"
PORT = 3000
uri = f"ws://{IP}:{PORT}"


async def update_lidar(data: list[float]):
    async with websockets.connect(uri + "/lidar", open_timeout=1) as websocket:
        # data = list(map(str, data))
        # data = "[" + ",".join(data) + "]"
        # await websocket.send("set$=$" + data)
        await websocket.send_json({"sender": "robot", "action": "set", "data": data})


async def update_log(data: str):
    async with websockets.connect(
        uri + "/log", open_timeout=1, ping_timeout=1
    ) as websocket:
        await websocket.send("update$=$[" + data + "]")


def update_log_sync(data: str):
    """
    Task to run on a new thread to update the log on the server

    Exemple :
    ```py
    from .API import update_log_sync
    from threading import Thread
    Thread(target=update_log_sync, args=("test",)).start()
    ```
    :param data: the data to send
    :type data: str
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    task = loop.create_task(update_log(data))
    try:
        loop.run_until_complete(task)
    except Exception as e:
        pass
    finally:
        loop.close()


async def get_last_command() -> tuple[str, list[float]] or None:
    """
    Get the last command sent to the robot by the RC
    Exemple :
    ```py
    from .API import get_last_command
    cmd, args = await get_last_command()
    if cmd == None:
        print("No command")
    else:
        print(f"Command : {cmd}, args : {args}")
    ```
    """

    async with websockets.connect(uri + "/cmd", open_timeout=1) as websocket:
        await websocket.send("get$=$")
        resp = await websocket.recv()
        if resp == "None" or resp == "error" or resp == "":
            return None
        else:
            cmd = resp[:4]
            args = None
            try:
                args = list(
                    map(float, resp[4:].replace("[", "").replace("]", "").split(","))
                )
            except IndexError:
                pass
            return cmd, args


async def send_action_finished(id: int):
    async with websockets.connect(uri + "/cmd", open_timeout=1) as websocket:
        await websocket.send(f"finished$=${str(id)}")


async def send_position(x: float, y: float, theta: float):
    async with websockets.connect(uri + "/position", open_timeout=1) as websocket:
        await websocket.send(f"set$=$[{x},{y},{theta}]")
