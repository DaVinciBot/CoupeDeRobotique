"""from bot import Logger, Lidar, Rolling_basis
from bot.api import update_lidar, get_last_command"""
from bot import Rolling_basis


"""import asyncio"""


def main():
    """
    Upload data for debug
    """
    
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
    """
    
    bot = Rolling_basis()


    
    
    destination = [10.0, 20.0]
    center = [5.0, 5.0]

    
    bot.curve_go_to(
        destination=destination,
        center=center,
        direction=True,
        speed=b'\x64',
        next_position_delay=100,
        action_error_auth=20,
        traj_precision=50
    )

if __name__ == "__main__":
    main()

    

# if __name__ == "__main__":
    #asyncio.run(main())