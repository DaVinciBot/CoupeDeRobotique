from config_loader import CONFIG
from logger import Logger, LogLevels
from arena import MarsArena
from geometry import Point
from controllers import Actuators
import matplotlib.pyplot as plt
from geometry import Point
from random import randint
from matplotlib.patches import Polygon as PolygonPatch
import asyncio  # Importer asyncio pour gérer les coroutines

def test_enable_go_to():
    logger = Logger()
    arena = MarsArena(
        1,
        logger,
        border_buffer=CONFIG.ARENA_CONFIG["border_buffer"],
        robot_buffer=CONFIG.ARENA_CONFIG["robot_buffer"],
    )

    x_start = []
    y_start = []
    x_stop = []
    y_stop = []
    for i in range(100):
        start = Point(randint(0, 200), randint(0, 300))
        stop = Point(randint(0, 200), randint(0, 300))
        if not arena.enable_go_to_point(start, stop):
            x_start.append(start.x)
            y_start.append(start.y)
            x_stop.append(stop.x)
            y_stop.append(stop.y)
            plt.plot([start.y, stop.y], [start.x, stop.x], color="black")

    forbidden_zone = arena.zones["forbidden"]
    if forbidden_zone:
        xy = forbidden_zone.exterior.coords.xy
        xy = list(zip(xy[1], xy[0]))
        patch = PolygonPatch(xy, facecolor="red", edgecolor="red", alpha=0.5, zorder=2)
        plt.gca().add_patch(patch)

    plt.xlim(0, 300)
    plt.ylim(200, 0)

    plt.scatter(y_start, x_start, color="blue", label="Start")
    plt.scatter(y_stop, x_stop, color="red", label="Stop")

    plt.xlabel("Y")
    plt.ylabel("X")
    plt.title("Forbidden Go-To")
    plt.legend()
    plt.show()


def test_compute_go_to():
    x_start = []
    y_start = []
    x_stop = []
    y_stop = []
    logger = Logger()
    arena = MarsArena(
        1,
        logger,
        border_buffer=CONFIG.ARENA_CONFIG["border_buffer"],
        robot_buffer=CONFIG.ARENA_CONFIG["robot_buffer"],
    )
    arena.zones["forbidden"] = None
    start = Point(100, 150)
    for i in range(len(arena.drop_zones)):
        stop = arena.compute_go_to_destination(start, arena.drop_zones[i].zone)
        x_start.append(start.x)
        y_start.append(start.y)
        x_stop.append(stop.x)
        y_stop.append(stop.y)

        if arena.enable_go_to_point(start, stop):
            plt.plot([start.y, stop.y], [start.x, stop.x], color="green")
        else:
            plt.plot([start.y, stop.y], [start.x, stop.x], color="red")

    plt.scatter(y_start, x_start, color="blue", label="Start")
    plt.scatter(y_stop, x_stop, color="red", label="Stop")
    plt.xlim(0, 300)
    plt.ylim(200, 0)
    plt.xlabel("Y")
    plt.ylabel("X")
    plt.title("Check Go_To auto_delta")
    plt.legend()
    plt.show()
    
async def test_lcd():
    logger = Logger()
    actuators = Actuators(logger, ser=14735440)
    await actuators.lcd_print("C'est des Barre mec test aajhvc;q kqscvqch qkhcvvc qkdjcvqkjdvckqjvc qkjdbvkqjbckjqd qkvbdqk")

def find_teensy_serial_numbers():
    import serial.tools.list_ports
    ports = serial.tools.list_ports.comports()
    print(ports.__len__())
    for port in ports:
        print(f"Serial Number: {port.serial_number}")

async def main():
    # test_enable_go_to()
    # test_compute_go_to()
    await test_lcd()  # Utiliser await pour exécuter la coroutine
    # find_teensy_serial_numbers()

if __name__ == "__main__":
    asyncio.run(main())
