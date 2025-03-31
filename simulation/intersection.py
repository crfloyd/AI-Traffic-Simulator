# simulation/intersection.py

import pygame

LIGHT_SIZE = 20

class Intersection:
    def __init__(self, grid_x, grid_y, cx, cy):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.cx = cx
        self.cy = cy

        # Light cycle config
        self.ns_duration = 5  # seconds
        self.ew_duration = 5
        self.all_red_duration = 2

        # Internal state
        self.phase = 'NS'  # 'NS', 'EW', or 'ALL_RED'
        self.elapsed = 0.0  # time in current phase

    def update(self, dt):
        self.elapsed += dt

        if self.phase == 'NS' and self.elapsed >= self.ns_duration:
            self.phase = 'ALL_RED'
            self.elapsed = 0
        elif self.phase == 'EW' and self.elapsed >= self.ew_duration:
            self.phase = 'ALL_RED'
            self.elapsed = 0
        elif self.phase == 'ALL_RED' and self.elapsed >= self.all_red_duration:
            self.phase = 'EW' if self.phase_before == 'NS' else 'NS'
            self.elapsed = 0

    @property
    def phase_before(self):
        return 'EW' if self.phase == 'NS' else 'NS'

    def draw(self, screen):
        # Draw intersection block
        pygame.draw.rect(screen, (160, 160, 160), (
            self.cx - 20,
            self.cy - 20,
            40,
            40
        ))

        # Show lights depending on current phase
        if self.phase == 'ALL_RED':
            ns_color = (255, 0, 0)
            ew_color = (255, 0, 0)
        elif self.phase == 'NS':
            ns_color = (0, 255, 0)
            ew_color = (255, 0, 0)
        else:  # 'EW'
            ns_color = (255, 0, 0)
            ew_color = (0, 255, 0)

        pygame.draw.circle(screen, ns_color, (self.cx, self.cy - 25), LIGHT_SIZE // 2)
        pygame.draw.circle(screen, ns_color, (self.cx, self.cy + 25), LIGHT_SIZE // 2)
        pygame.draw.circle(screen, ew_color, (self.cx - 25, self.cy), LIGHT_SIZE // 2)
        pygame.draw.circle(screen, ew_color, (self.cx + 25, self.cy), LIGHT_SIZE // 2)
