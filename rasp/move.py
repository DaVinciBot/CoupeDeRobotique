from bot import Logger, Rolling_basis
import asyncio

def main():
    SPEED = b'\x50'
    com = Rolling_basis(crc=False)  
    while True:
        test = input("Enter command: ")
        if test == "f":
            com.Go_To([20, 0, 0], speed=SPEED)
        elif test == "b":
            com.Go_To([-20, 0, 0], speed=SPEED)
        elif test == "l":
            com.Go_To([0, 20, 0], speed=SPEED)
        elif test == "r":
            com.Go_To([0, -20, 0], speed=SPEED)
            
if __name__ == "__main__":
    main()
    
        