from bot import Logger, Lidar
from bot.api import update_lidar

import asyncio


async def main():
    """
    Upload data for debug
    """
    lidar = Lidar.Lidar()
    l = Logger()
    await l.log('Logger initialized')
    while True:
        val = lidar.get_values()
        await update_lidar(val)

if __name__ == "__main__":
    asyncio.run(main())