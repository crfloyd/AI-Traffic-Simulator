
import pygame

GRID_SIZE = 3
CELL_SIZE = 200
ROAD_WIDTH = 40
LIGHT_SIZE = 20
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 800
SIDEBAR_WIDTH = 200

class Grid:
    def __init__(self):
        self.grid_size = GRID_SIZE
        self.grid_width = CELL_SIZE * self.grid_size
        self.grid_height = CELL_SIZE * self.grid_size

        # Offset so the grid is centered in the main area (excluding sidebar)
        self.offset_x = (WINDOW_WIDTH - SIDEBAR_WIDTH - self.grid_width) // 2
        self.offset_y = (WINDOW_HEIGHT - self.grid_height) // 2

    def draw(self, screen):
        # 1. Draw all horizontal roads (rows)
        for row in range(self.grid_size):
            cy = self.offset_y + row * CELL_SIZE + CELL_SIZE // 2
            pygame.draw.rect(screen, (100, 100, 100), (
                self.offset_x,
                cy - ROAD_WIDTH // 2,
                self.grid_width,
                ROAD_WIDTH
            ))

        # 2. Draw all vertical roads (columns)
        for col in range(self.grid_size):
            cx = self.offset_x + col * CELL_SIZE + CELL_SIZE // 2
            pygame.draw.rect(screen, (100, 100, 100), (
                cx - ROAD_WIDTH // 2,
                0,
                ROAD_WIDTH,
                WINDOW_HEIGHT
            ))

        # 3. Draw intersections
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                cx = self.offset_x + col * CELL_SIZE + CELL_SIZE // 2
                cy = self.offset_y + row * CELL_SIZE + CELL_SIZE // 2

                # Intersection block
                pygame.draw.rect(screen, (160, 160, 160), (
                    cx - ROAD_WIDTH,
                    cy - ROAD_WIDTH,
                    ROAD_WIDTH * 2,
                    ROAD_WIDTH * 2
                ))

                # Placeholder traffic lights
                pygame.draw.circle(screen, (0, 255, 0), (cx + 30, cy - 30), LIGHT_SIZE // 2)
                pygame.draw.circle(screen, (255, 0, 0), (cx - 30, cy + 30), LIGHT_SIZE // 2)
