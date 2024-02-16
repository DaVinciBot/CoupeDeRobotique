##################################################
# CE SCRIPT PERMET SIMPLEMENT DE TESTER LE ROBOT #
#  IL SE CONNECTE A L'INTERFACE WEB, ENVOIE LES  #
#    DONNEES DU LIDAR ET RECOIT DES COMMANDES    #
##################################################


from bot import Logger, Lidar, RollingBasis
from bot.API import update_lidar, get_last_command, send_action_finished, send_position

import asyncio


async def main():
    """
    Upload and receive data for debug
    """
    lidar = Lidar()
    l = Logger()
    robot = RollingBasis()
    #await l.log("Logger initialized")
    while True:
        try:
            tmp = await get_last_command()
            if tmp != None and robot.action_finished:
                cmd, args = tmp
                if cmd == "goto":
                    robot.Go_To(args, speed=b"\x50")
                elif cmd == "home":
                    robot.Set_Home()
                elif cmd == "dpid":
                    robot.Disable_Pid()
                elif cmd == "epid":
                    robot.Enable_Pid()
                elif cmd == "kpos":
                    robot.Keep_Current_Position()

            if robot.action_finished:
                await send_action_finished()
        except: pass

        val = lidar.get_values()
        await update_lidar(val)
        await send_position(robot.odometrie.x, robot.odometrie.y, robot.odometrie.theta)


if __name__ == "__main__":
    asyncio.run(main())
