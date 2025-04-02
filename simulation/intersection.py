# simulation/intersection.py

import pygame
import random

LIGHT_SIZE = 20

class Intersection:
    def __init__(self, grid_x, grid_y, cx, cy):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.cx = cx
        self.cy = cy
        self.rect = pygame.Rect(cx - 20, cy - 20, 40, 40)

        self.phase = 'NS'
        self.last_phase = 'NS'
        self.elapsed = random.uniform(0, 5)  # ✨ Desync phase start time

        self.ns_duration = 5
        self.ew_duration = 5
        self.all_red_duration = 1

        self.just_updated = False
        self.updated_timer = 0.0
        self.waiting_cars = 0

        self.queues = {"N": 0, "S": 0, "E": 0, "W": 0}



    def update(self, dt):
        self.elapsed += dt
        
        if self.elapsed == 0:  # Light just changed
            print(f"[{self.grid_x}, {self.grid_y}] -> Phase changed to {self.phase}")


        if self.phase == 'NS' and self.elapsed >= self.ns_duration:
            self.phase = 'ALL_RED'
            self.last_phase = 'NS'
            self.elapsed = 0
        elif self.phase == 'EW' and self.elapsed >= self.ew_duration:
            self.phase = 'ALL_RED'
            self.last_phase = 'EW'
            self.elapsed = 0
        elif self.phase == 'ALL_RED' and self.elapsed >= self.all_red_duration:
            self.phase = 'EW' if self.last_phase == 'NS' else 'NS'
            self.elapsed = 0
            
        if self.just_updated:
            self.updated_timer -= dt
            if self.updated_timer <= 0:
                self.just_updated = False



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
        
        if self.just_updated:
            pygame.draw.rect(screen, (255, 255, 100), self.rect.inflate(6, 6), border_radius=8)

        pygame.draw.circle(screen, ns_color, (self.cx, self.cy - 25), LIGHT_SIZE // 2)
        pygame.draw.circle(screen, ns_color, (self.cx, self.cy + 25), LIGHT_SIZE // 2)
        pygame.draw.circle(screen, ew_color, (self.cx - 25, self.cy), LIGHT_SIZE // 2)
        pygame.draw.circle(screen, ew_color, (self.cx + 25, self.cy), LIGHT_SIZE // 2)

    def mark_updated(self):
        self.just_updated = True
        self.updated_timer = 1.5  # seconds
