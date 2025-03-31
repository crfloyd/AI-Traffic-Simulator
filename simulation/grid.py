# simulation/grid.py

import pygame
from simulation.intersection import Intersection
from simulation.car import Car

GRID_SIZE = 3
CELL_SIZE = 200
ROAD_WIDTH = 40
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 800
SIDEBAR_WIDTH = 200

class Grid:
    def __init__(self):
        self.grid_size = GRID_SIZE
        self.grid_width = CELL_SIZE * self.grid_size
        self.grid_height = CELL_SIZE * self.grid_size

        self.offset_x = (WINDOW_WIDTH - SIDEBAR_WIDTH - self.grid_width) // 2
        self.offset_y = (WINDOW_HEIGHT - self.grid_height) // 2
        
        self.cars = []
        self.cars.append(Car(self.offset_x + CELL_SIZE // 2, WINDOW_HEIGHT, "N"))
        self.cars.append(Car(self.offset_x + 2 * CELL_SIZE + CELL_SIZE // 2, 0, "S"))
        self.cars.append(Car(0, self.offset_y + CELL_SIZE + CELL_SIZE // 2, "E"))
        self.cars.append(Car(WINDOW_WIDTH - SIDEBAR_WIDTH, self.offset_y + 2 * CELL_SIZE + CELL_SIZE // 2, "W"))

        self.intersections = []
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                cx = self.offset_x + col * CELL_SIZE + CELL_SIZE // 2
                cy = self.offset_y + row * CELL_SIZE + CELL_SIZE // 2
                self.intersections.append(Intersection(col, row, cx, cy))

    def draw(self, screen):
        # Draw horizontal roads
        for row in range(self.grid_size):
            cy = self.offset_y + row * CELL_SIZE + CELL_SIZE // 2
            pygame.draw.rect(screen, (100, 100, 100), (
                self.offset_x,
                cy - ROAD_WIDTH // 2,
                self.grid_width,
                ROAD_WIDTH
            ))

        # Draw vertical roads
        for col in range(self.grid_size):
            cx = self.offset_x + col * CELL_SIZE + CELL_SIZE // 2
            pygame.draw.rect(screen, (100, 100, 100), (
                cx - ROAD_WIDTH // 2,
                0,
                ROAD_WIDTH,
                WINDOW_HEIGHT
            ))

        # Draw intersections
        for intersection in self.intersections:
            intersection.draw(screen)
            
        for car in self.cars:
            car.update()
            car.draw(screen)
