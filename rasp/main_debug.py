from bot import Rolling_basis

def main():
    robot = Rolling_basis()
    while True:
        print("Enter command :")
        cmd = input()
        if cmd == "goto":
            print("Enter X :")
            x = float(input())
            print("Enter Y :")
            y = float(input())
            robot.Go_To((x, y, 0.0))
        elif cmd == "home":
            robot.Set_Home()
        elif cmd == "dpid":
            robot.Disable_Pid()
        elif cmd == "epid":
            robot.Enable_Pid()
        elif cmd == "kpos":
            robot.Keep_Current_Position()
        elif cmd == "exit":
            break
        else:
            print("Unknown command")
            
if __name__ == "__main__":
    main()