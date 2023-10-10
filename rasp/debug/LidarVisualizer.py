import pygame
import pygame_gui
import math
import random
import time

import requests


class LidarVisualizer:

    def __init__(self) -> None:
        self.lidar_data = []

    def show(self):
        pygame.init()
        
        self.update_data()

        pygame.display.set_caption("Lidar Visualizer - CDR 2023")
        window_surface = pygame.display.set_mode((800, 600))

        background = pygame.Surface((800, 600))
        background.fill(pygame.Color("#000000"))

        manager = pygame_gui.UIManager((800, 600))

        clock = pygame.time.Clock()
        is_running = True

        # dummy_data = [250 * random.random() for i in range(810)]

        rotate = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((350, 550), (100, 50)),
            text="Rotate",
            manager=manager,
        )
        rotation = (3 * math.pi) / 4

        while is_running:
            # clear the screen
            background.fill(pygame.Color("#000000"))

            self.update_data()

            time_delta = clock.tick(10) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    is_running = False

                if event.type == pygame.USEREVENT:
                    if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                        if event.ui_element == rotate:
                            rotation += math.pi / 4
                            rotation %= 2 * math.pi

                manager.process_events(event)

            manager.update(time_delta)

            # lidar data are in polar coordinates, we need to convert them to cartesian coordinates
            for i in range(len(self.lidar_data)):
                if self.lidar_data[i] > 0:
                    pygame.draw.line(
                        background,
                        pygame.Color("#FFFFFF"),
                        (400, 300),
                        (
                            400
                            + self.lidar_data[i] * 25 * math.cos(math.radians(i / 3) + rotation),
                            300
                            + self.lidar_data[i] * 25 * math.sin(math.radians(i / 3) + rotation),
                        ),
                    )
                else:
                    pygame.draw.line(
                        background,
                        pygame.Color("#FFFFFF"),
                        (400, 300),
                        (
                            400
                            + 10 * 25 * math.cos(math.radians(i / 3) + rotation),
                            300
                            + 10 * 25 * math.sin(math.radians(i / 3) + rotation),
                        ),
                    )

            # Add red cirlce to represent the limit of the field
            pygame.draw.circle(background, pygame.Color("#FF0000"), (400, 300), 250, 1)
            # Add solid red circle to represent the robot
            pygame.draw.circle(background, pygame.Color("#FF0000"), (400, 300), 15)

            window_surface.blit(background, (0, 0))
            manager.draw_ui(window_surface)
            pygame.display.update()

    def update_data(self):
        # fetch data from /api/lidar
        response = requests.get("http://robot1:5000/api/lidar")
        self.lidar_data = [float(el) for el in response.text.replace("[", "").replace("]", "").replace('"', "").split(",")]
        time.sleep(0.1)


if __name__ == "__main__":
    visualizer = LidarVisualizer()
    visualizer.show()