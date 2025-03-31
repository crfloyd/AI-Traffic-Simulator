import pygame

LIGHT_SIZE = 20

class Intersection:
    def __init__(self, grid_x, grid_y, cx, cy):
        self.grid_x = grid_x  # column index
        self.grid_y = grid_y  # row index
        self.cx = cx
        self.cy = cy
        self.phase = 'NS'  # NS or EW
        self.timer = 0  # placeholder for switching logic

    def toggle(self):
        self.phase = 'EW' if self.phase == 'NS' else 'NS'

    def draw(self, screen):
        # Draw intersection square
        pygame.draw.rect(screen, (160, 160, 160), (
            self.cx - 20,
            self.cy - 20,
            40,
            40
        ))

        # Green in current direction, red in the other
        ns_color = (0, 255, 0) if self.phase == 'NS' else (255, 0, 0)
        ew_color = (0, 255, 0) if self.phase == 'EW' else (255, 0, 0)

        pygame.draw.circle(screen, ns_color, (self.cx, self.cy - 25), LIGHT_SIZE // 2)
        pygame.draw.circle(screen, ns_color, (self.cx, self.cy + 25), LIGHT_SIZE // 2)
        pygame.draw.circle(screen, ew_color, (self.cx - 25, self.cy), LIGHT_SIZE // 2)
        pygame.draw.circle(screen, ew_color, (self.cx + 25, self.cy), LIGHT_SIZE // 2)
