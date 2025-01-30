import pygame
import sys
from remote import PS5Remote


class RemoteSimulator:
    def __init__(self, remote):
        self.remote: PS5Remote = remote
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

            self.remote.update()

            self.screen.fill(self.WHITE)

            arrow_angle = self.remote.angle * 180 / 3.141592653589793

            self.draw_arrow(self.screen, self.BLACK, self.arrow_pos, arrow_angle)

            font = pygame.font.Font(None, 36)
            angle_text = font.render(f"Angle: {arrow_angle:.1f}°", True, self.BLACK)
            x, y = self.remote.get_joystick_input()
            joystick_text = font.render(
                f"Joystick: ({x:.2f}, {y:.2f})", True, self.BLACK
            )
            rotation_sensitivity_text = font.render(
                f"Rotation Sensitivity: {self.remote.rotation_speed_sensitivity:.2f}",
                True,
                self.BLACK,
            )
            rotation_speed_text = font.render(
                f"Linear Speed: {self.remote.current_linear_speed:.2f}",
                True,
                self.BLACK,
            )
            linear_speed_text = font.render(
                f"Rotation Speed: {self.remote.current_rotation_speed:.2f}",
                True,
                self.BLACK,
            )

            self.screen.blit(angle_text, (10, 10))
            self.screen.blit(joystick_text, (10, 50))
            self.screen.blit(rotation_sensitivity_text, (10, 90))
            self.screen.blit(rotation_speed_text, (10, 130))
            self.screen.blit(linear_speed_text, (10, 170))

            pygame.display.flip()
            self.clock.tick(self.FPS)

        self.remote.disconnect()
        pygame.quit()
        sys.exit()
