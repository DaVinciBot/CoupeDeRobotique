import pygame
import sys
from pydualsense import pydualsense


class Remote:
    def __init__(
        self, sensitivity=1, max_rotation_speed=10.0, smoothing_factor=0.2, deadzone=15
    ):
        self.dualsense = pydualsense()
        self.dualsense.init()
        self.sensitivity = sensitivity
        self.max_rotation_speed = max_rotation_speed
        self.smoothing_factor = smoothing_factor
        self.current_rotation_speed = 0.0
        self.deadzone = deadzone
        self.arrow_angle = 0

    def get_joystick_input(self):
        """Retrieves joystick values and normalizes them in [-1,1]."""
        x = self.dualsense.state.RX  # Raw value (-128 to 128)
        y = self.dualsense.state.RY

        if abs(x) < self.deadzone:
            x = 0
        if abs(y) < self.deadzone:
            y = 0

        return x / 128.0, y / 128.0

    def update_angle(self):
        x, _ = self.get_joystick_input()
        target_rotation_speed = x * self.max_rotation_speed * self.sensitivity
        self.current_rotation_speed += (
            target_rotation_speed - self.current_rotation_speed
        ) * self.smoothing_factor
        self.arrow_angle = (self.arrow_angle + self.current_rotation_speed) % 360

    def close(self):
        self.dualsense.close()


class Game:
    def __init__(self, remote):
        self.remote = remote
        self.WIDTH, self.HEIGHT = 800, 600
        self.FPS = 60
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.arrow_pos = [self.WIDTH // 2, self.HEIGHT // 2]
        pygame.init()
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Control the arrow with the PS5 controller")
        self.clock = pygame.time.Clock()

    def draw_arrow(self, surface, color, position, angle):
        """Draws an arrow at the given position with the specified angle."""
        arrow_length = 50
        arrow_width = 20
        arrow = pygame.Surface((arrow_length, arrow_width), pygame.SRCALPHA)
        pygame.draw.polygon(
            arrow, color, [(0, 0), (arrow_length, arrow_width // 2), (0, arrow_width)]
        )
        rotated_arrow = pygame.transform.rotate(arrow, -angle)
        surface.blit(rotated_arrow, rotated_arrow.get_rect(center=position))

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.remote.update_angle()

            self.screen.fill(self.WHITE)
            self.draw_arrow(
                self.screen, self.BLACK, self.arrow_pos, self.remote.arrow_angle
            )

            font = pygame.font.Font(None, 36)
            angle_text = font.render(
                f"Angle: {self.remote.arrow_angle:.1f}°", True, self.BLACK
            )
            x, y = self.remote.get_joystick_input()
            joystick_text = font.render(
                f"Joystick: ({x:.2f}, {y:.2f})", True, self.BLACK
            )
            sensitivity_text = font.render(
                f"Sensitivity: {self.remote.sensitivity:.2f}", True, self.BLACK
            )
            speed_text = font.render(
                f"Rotation Speed: {self.remote.current_rotation_speed:.2f}",
                True,
                self.BLACK,
            )

            self.screen.blit(angle_text, (10, 10))
            self.screen.blit(joystick_text, (10, 50))
            self.screen.blit(sensitivity_text, (10, 90))
            self.screen.blit(speed_text, (10, 130))

            pygame.display.flip()
            self.clock.tick(self.FPS)

        self.remote.close()
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    remote = Remote()
    game = Game(remote)
    game.run()
