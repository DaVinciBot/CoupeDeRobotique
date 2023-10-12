from bot import Logger, Rolling_basis, Lidar
from bot.api import update_lidar, handle_command
import time

import asyncio

async def lidar_loop(lidar):
    while True:
        time.sleep(0.016)
        val = lidar.get_values()
        await update_lidar(val) # update lidar data on the server

async def main():
    lidar = Lidar.Lidar()
    
    com = Rolling_basis(crc=False)    
    l =  Logger()
    await l.log('Logger initialized')
    await handle_command(com)
    l.log('command handler started')
    await lidar_loop(lidar)
    l.log('lidar loop started')


if __name__ == "__main__":
    asyncio.run(main())
