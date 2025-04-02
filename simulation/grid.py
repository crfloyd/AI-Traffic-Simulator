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
    def __init__(self, headless=False):
        self.headless = headless
        self.grid_size = GRID_SIZE
        self.grid_width = CELL_SIZE * self.grid_size
        self.grid_height = CELL_SIZE * self.grid_size

        self.offset_x = (WINDOW_WIDTH - SIDEBAR_WIDTH - self.grid_width) // 2
        self.offset_y = (WINDOW_HEIGHT - self.grid_height) // 2
        
        self.cars = []
        self.spawn_timer = 0.0
        self.spawn_interval = 0.6 if headless else 2.0   # seconds between spawns
        
        self.total_wait_time = 0.0
        self.cars_processed = 0
        self.avg_wait_time = 0.0
        self.fitness = 0.0

        self.road_speed_limits = {
            "horizontal": {},  # key = (row, col) for EW roads
            "vertical": {}     # key = (row, col) for NS roads
        }


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

        # Reset per-intersection congestion counts
        for intersection in self.intersections:
            intersection.waiting_cars = 0

        # Update and draw intersections
        for intersection in self.intersections:
            intersection.update(dt)
            intersection.draw(screen)

        # Update and draw cars
        for car in self.cars:
            car.update(self.intersections, dt, self.cars)
            car.draw(screen)
            nearest = car.get_nearest_intersection(self.intersections)
            if car.state == "waiting" and nearest:
                nearest.waiting_cars += 1

        # Remove cars off-screen
        remaining_cars = []
        for c in self.cars:
            if -50 <= c.x <= WINDOW_WIDTH - SIDEBAR_WIDTH + 50 and -50 <= c.y <= WINDOW_HEIGHT + 50:
                remaining_cars.append(c)
            else:
                self.total_wait_time += c.stopped_time
                self.cars_processed += 1

        self.cars = remaining_cars

        # Avoid div by zero
        if self.cars_processed > 0:
            self.avg_wait_time = self.total_wait_time / self.cars_processed
        else:
            self.avg_wait_time = 0.0

        # Spawn new cars
        self.spawn_timer += dt
        if self.headless:
            while self.spawn_timer >= self.spawn_interval:
                self.spawn_car()
                self.spawn_timer -= self.spawn_interval
        else:
            if self.spawn_timer >= self.spawn_interval:
                self.spawn_car()
                self.spawn_timer = 0

        # Congestion metrics
        stopped_cars = sum(1 for c in self.cars if c.stopped_time > 10.0)
        queued_cars = len(self.cars)
        intersection_congestion = sum(i.waiting_cars for i in self.intersections)
        heavy_congestion_penalty = max(0, queued_cars - 20)

        self.fitness = (
            0.5 * self.avg_wait_time +
            2.0 * stopped_cars +
            0.1 * heavy_congestion_penalty +
            0.05 * intersection_congestion
        )
        self.total_congestion = sum(i.waiting_cars for i in self.intersections)


            
    def spawn_car(self):
        edge = random.choice(["N", "S", "E", "W"])

        if edge == "N":
            col = random.choice(range(self.grid_size))
            x = self.offset_x + col * CELL_SIZE + CELL_SIZE // 2
            y = WINDOW_HEIGHT
            direction = "N"
        elif edge == "S":
            col = random.choice(range(self.grid_size))
            x = self.offset_x + col * CELL_SIZE + CELL_SIZE // 2
            y = 0
            direction = "S"
        elif edge == "E":
            row = random.choice(range(self.grid_size))
            x = 0
            y = self.offset_y + row * CELL_SIZE + CELL_SIZE // 2
            direction = "E"
        elif edge == "W":
            row = random.choice(range(self.grid_size))
            x = WINDOW_WIDTH - SIDEBAR_WIDTH
            y = self.offset_y + row * CELL_SIZE + CELL_SIZE // 2
            direction = "W"

        # Check if there's enough space in that lane
        spawn_gap = 50  # You can tweak this if needed
        for car in self.cars:
            if car.direction != direction:
                continue
            if direction == "N" and abs(car.x - x) < 10 and car.y > y - spawn_gap:
                return  # Block spawn
            if direction == "S" and abs(car.x - x) < 10 and car.y < y + spawn_gap:
                return
            if direction == "E" and abs(car.y - y) < 10 and car.x < x + spawn_gap:
                return
            if direction == "W" and abs(car.y - y) < 10 and car.x > x - spawn_gap:
                return

        # If clear, spawn
        from simulation.car import Car
        acceleration = random.uniform(40.0, 70.0)
        max_speed = random.uniform(80.0, 100.0)
        self.cars.append(Car(x, y, direction, max_speed=max_speed, acceleration=acceleration, initial_speed=max_speed))




