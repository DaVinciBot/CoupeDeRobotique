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
    Points = [(0, 0, 0), (20, 0, 0), (0, 20, 0), (-20, 0, 0), (0, -20, 0)]
    l =  Logger()
    await l.log('Logger initialized')
    i = 0
    await l.log(f"new action: {i}")
    com.Go_To(Points[i])
    i+=1
    dt = 0 
    while True:
        dt += 1
        val = lidar.get_values()
        await update_lidar(val)
        if dt % 300 == 0:
            if i == len(Points):
                return
            await l.log(f"new action: {i}")
            com.Go_To(Points[i], speed=b'\x40')
            i+=1
            
        

if __name__ == "__main__":
    asyncio.run(main())
