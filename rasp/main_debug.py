from bot import Logger, Lidar, Rolling_basis
from bot.api import update_lidar, get_last_command

import asyncio


async def main():
    """
    Upload data for debug
    """
    lidar = Lidar()
    l = Logger()
    robot = Rolling_basis(crc=False)
    await l.log('Logger initialized')
    while True:
        cmd, args = await get_last_command()
        if cmd is not None:
            await l.log(cmd)
            if cmd == "forward":
                robot.Go_To(args, speed=b"\x50")
        val = lidar.get_values()
        await update_lidar(val)

if __name__ == "__main__":
    asyncio.run(main())