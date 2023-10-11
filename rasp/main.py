from bot import Logger, Utils, GPIO, Rolling_basis, Lidar
from bot.api import update_lidar
import time

import asyncio



async def main():
    state = Utils.load_state()

    lidar = Lidar.Lidar()
    
    com = Rolling_basis(crc=False)
    #com.Go_To([10, 100, 0]) ça fonctione peut etre 
    
    l =  Logger()
    await l.log('Logger initialized')
    tirette_pin = GPIO.PIN(37, "INPUT")
    led_pin = GPIO.PIN(8, "OUTPUT")
    state.set("tirette", "0")
    state.set("led", "0")

    while True:
            
        state.set("led", str(led_pin.get()))
        state.set("tirette", str(tirette_pin.get()))

        val = lidar.get_values()
        try:
            await update_lidar(val) # update lidar data on the server
        except:
            pass
        await l.log('lidar update')


if __name__ == "__main__":
    asyncio.run(main())
