import pygame
import random
from simulation.intersection import Intersection
from simulation.car import Car

GRID_ROWS = 3  # Vertical roads
GRID_COLS = 5  # Horizontal roads (more to simulate main arteries)
ROAD_WIDTH = 40
SIDEBAR_WIDTH = 200
CAR_SPEED = 140
CAR_ACCEL = 50

class Grid:
    def __init__(self, headless=False):
        self.headless = headless

        # Get current display size for dynamic layout
        info = pygame.display.Info()
        self.window_width = info.current_w
        self.window_height = info.current_h

        self.grid_width = self.window_width - SIDEBAR_WIDTH
        self.grid_height = self.window_height

        self.cell_width = self.grid_width // GRID_COLS
        self.cell_height = self.grid_height // GRID_ROWS

        self.offset_x = (self.grid_width - self.cell_width * GRID_COLS) // 2
        self.offset_y = (self.grid_height - self.cell_height * GRID_ROWS) // 2

        self.cars = []
        self.spawn_timer = 0.0
        self.spawn_interval = 0.6 if headless else 2.0

        self.total_wait_time = 0.0
        self.cars_processed = 0
        self.avg_wait_time = 0.0
        self.fitness = 0.0

        self.road_speed_limits = {
            "horizontal": {},
            "vertical": {}
        }

        for row in range(GRID_ROWS):
            for col in range(GRID_COLS - 1):
                self.road_speed_limits["horizontal"][(row, col)] = 1.0  # Fast road

        for row in range(GRID_ROWS - 1):
            for col in range(GRID_COLS):
                self.road_speed_limits["vertical"][(row, col)] = 0.5  # Slower road

        self.intersections = []
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                cx = self.offset_x + col * self.cell_width + self.cell_width // 2
                cy = self.offset_y + row * self.cell_height + self.cell_height // 2
                self.intersections.append(Intersection(col, row, cx, cy))

    def get_speed_limit(self, car):
        if car.direction in ("E", "W"):
            row = round((car.y - self.offset_y - self.cell_height // 2) / self.cell_height)
            col = int((car.x - self.offset_x) // self.cell_width)
            return self.road_speed_limits["horizontal"].get((row, col), 1.0)
        else:
            col = round((car.x - self.offset_x - self.cell_width // 2) / self.cell_width)
            row = int((car.y - self.offset_y) // self.cell_height)
            return self.road_speed_limits["vertical"].get((row, col), 1.0)

    def draw(self, screen, dt):
        for row in range(GRID_ROWS):
            cy = self.offset_y + row * self.cell_height + self.cell_height // 2
            pygame.draw.rect(screen, (100, 100, 100), (
                self.offset_x,
                cy - ROAD_WIDTH // 2,
                self.grid_width,
                ROAD_WIDTH
            ))

        for col in range(GRID_COLS):
            cx = self.offset_x + col * self.cell_width + self.cell_width // 2
            pygame.draw.rect(screen, (100, 100, 100), (
                cx - ROAD_WIDTH // 2,
                0,
                ROAD_WIDTH,
                self.grid_height
            ))

        for inter in self.intersections:
            inter.waiting_cars = 0
            inter.update(dt)
            inter.draw(screen)

        for car in self.cars:
            car.road_speed_factor = self.get_speed_limit(car)
            car.update(self.intersections, dt, self.cars)
            car.draw(screen)
            nearest = car.get_nearest_intersection(self.intersections)
            if car.state == "waiting" and nearest:
                nearest.waiting_cars += 1

        remaining = []
        for c in self.cars:
            if -50 <= c.x <= self.window_width - SIDEBAR_WIDTH + 50 and -50 <= c.y <= self.window_height + 50:
                remaining.append(c)
            else:
                self.total_wait_time += c.stopped_time
                self.cars_processed += 1
        self.cars = remaining

        if self.cars_processed > 0:
            self.avg_wait_time = self.total_wait_time / self.cars_processed
        else:
            self.avg_wait_time = 0.0

        self.spawn_timer += dt
        if self.headless:
            while self.spawn_timer >= self.spawn_interval:
                self.spawn_car()
                self.spawn_timer -= self.spawn_interval
        else:
            if self.spawn_timer >= self.spawn_interval:
                self.spawn_car()
                self.spawn_timer = 0

        stopped = sum(1 for c in self.cars if c.stopped_time > 10.0)
        queued = len(self.cars)
        intersection_congestion = sum(i.waiting_cars for i in self.intersections)
        heavy_congestion_penalty = max(0, queued - 20)

        self.fitness = (
            0.5 * self.avg_wait_time +
            2.0 * stopped +
            0.1 * heavy_congestion_penalty +
            0.05 * intersection_congestion
        )
        self.total_congestion = intersection_congestion

    def spawn_car(self):
        edge = random.choices(["N", "S", "E", "W"], weights=[1, 1, 3, 3])[0]

        if edge == "N":
            col = random.choice(range(GRID_COLS))
            x = self.offset_x + col * self.cell_width + self.cell_width // 2
            y = self.window_height
            direction = "N"
        elif edge == "S":
            col = random.choice(range(GRID_COLS))
            x = self.offset_x + col * self.cell_width + self.cell_width // 2
            y = 0
            direction = "S"
        elif edge == "E":
            row = random.choice(range(GRID_ROWS))
            x = 0
            y = self.offset_y + row * self.cell_height + self.cell_height // 2
            direction = "E"
        elif edge == "W":
            row = random.choice(range(GRID_ROWS))
            x = self.window_width - SIDEBAR_WIDTH
            y = self.offset_y + row * self.cell_height + self.cell_height // 2
            direction = "W"

        self.cars.append(Car(x, y, direction, max_speed=CAR_SPEED, acceleration=CAR_ACCEL))
