# simulation/grid.py

import pygame
import random
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
        self.spawn_timer = 0.0
        self.spawn_interval = 2.0  # seconds between spawns
        # self.cars.append(Car(self.offset_x + CELL_SIZE // 2, WINDOW_HEIGHT, "N"))
        # self.cars.append(Car(self.offset_x + 2 * CELL_SIZE + CELL_SIZE // 2, 0, "S"))
        # self.cars.append(Car(0, self.offset_y + CELL_SIZE + CELL_SIZE // 2, "E"))
        # self.cars.append(Car(WINDOW_WIDTH - SIDEBAR_WIDTH, self.offset_y + 2 * CELL_SIZE + CELL_SIZE // 2, "W"))

        self.intersections = []
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                cx = self.offset_x + col * CELL_SIZE + CELL_SIZE // 2
                cy = self.offset_y + row * CELL_SIZE + CELL_SIZE // 2
                self.intersections.append(Intersection(col, row, cx, cy))

    def draw(self, screen, dt):
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

        # Update and draw intersections
        for intersection in self.intersections:
            intersection.update(dt)
            intersection.draw(screen)

        # Update and draw cars
        for car in self.cars:
            car.update(self.intersections, dt)
            car.draw(screen)

        # Remove cars off-screen
        self.cars = [c for c in self.cars if 0 <= c.x <= 600 and 0 <= c.y <= 800]

        # Spawn new cars
        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_car()
            self.spawn_timer = 0
            
    def spawn_car(self):
        edge = random.choice(["N", "S", "E", "W"])

        if edge == "N":
            x = self.offset_x + random.choice(range(self.grid_size)) * CELL_SIZE + CELL_SIZE // 2
            y = WINDOW_HEIGHT
            direction = "N"
        elif edge == "S":
            x = self.offset_x + random.choice(range(self.grid_size)) * CELL_SIZE + CELL_SIZE // 2
            y = 0
            direction = "S"
        elif edge == "E":
            x = 0
            y = self.offset_y + random.choice(range(self.grid_size)) * CELL_SIZE + CELL_SIZE // 2
            direction = "E"
        elif edge == "W":
            x = WINDOW_WIDTH - SIDEBAR_WIDTH
            y = self.offset_y + random.choice(range(self.grid_size)) * CELL_SIZE + CELL_SIZE // 2
            direction = "W"

        from simulation.car import Car
        self.cars.append(Car(x, y, direction))

