# simulation/intersection.py

import pygame
import random

LIGHT_SIZE = 20

class Intersection:
    def __init__(self, grid_x, grid_y, cx, cy, num_rows, num_cols):
        self.col = grid_x
        self.row = grid_y
        self.cx = cx
        self.cy = cy
        self.rect = pygame.Rect(cx - 20, cy - 20, 40, 40)

        self.num_rows = num_rows
        self.num_cols = num_cols

        self.phase = 'NS'
        self.last_phase = 'NS'
        self.elapsed = random.uniform(0, 5)  # ✨ Desync phase start time

        self.ns_duration = 5
        self.ew_duration = 5
        self.all_red_duration = 1

        self.just_updated = False
        self.updated_timer = 0.0
        self.waiting_cars = 0
        self.waiting_time_total = 0.0  # Total wait time of cars near this intersection in this run

        self.queues = {"N": 0, "S": 0, "E": 0, "W": 0}



    def update(self, dt):
        self.elapsed += dt
        
        # if self.elapsed == 0:  # Light just changed
        #     print(f"[{self.grid_x}, {self.grid_y}] -> Phase changed to {self.phase}")


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
        # Intersection box
        pygame.draw.rect(screen, (150, 150, 150), (self.cx - 20, self.cy - 20, 40, 40))

        # RED = (255, 0, 0), GREEN = (0, 255, 0)
        ns_color = (0, 255, 0) if self.phase == "NS" else (255, 0, 0)
        ew_color = (0, 255, 0) if self.phase == "EW" else (255, 0, 0)

        # Draw vertical lights (north/south)
        if self.row > 0:  # Show north light only if not in top row
            pygame.draw.circle(screen, ns_color, (self.cx, self.cy - 30), 6)
        if self.row < self.num_rows - 1:  # Show south light only if not in bottom row
            pygame.draw.circle(screen, ns_color, (self.cx, self.cy + 30), 6)

        # Draw horizontal lights (east/west)
        if self.col > 0:  # Show west light only if not in first column
            pygame.draw.circle(screen, ew_color, (self.cx - 30, self.cy), 6)
        if self.col < self.num_cols - 1:  # Show east light only if not in last column
            pygame.draw.circle(screen, ew_color, (self.cx + 30, self.cy), 6)

    def mark_updated(self):
        self.just_updated = True
        self.updated_timer = 1.5  # seconds

    def reset(self):
        self.waiting_cars = 0
        self.waiting_time_total = 0.0
