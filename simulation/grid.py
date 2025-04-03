import pygame
import random
from simulation.intersection import Intersection
from simulation.car import Car

GRID_ROWS = 4
GRID_COLS = 5
ROAD_WIDTH = 40
SIDEBAR_WIDTH = 200
CAR_SPEED = 140
CAR_ACCEL = 50
SCREEN_MARGIN = 60
HEAVY_CONGESTION_THRESHOLD = 15
SPILLOVER_THRESHOLD = 5


class Grid:
    def __init__(self, headless=False):
        self.headless = headless

        info = pygame.display.Info()
        self.window_width = info.current_w
        self.window_height = info.current_h

        self.grid_width = self.window_width - SIDEBAR_WIDTH
        self.grid_height = self.window_height

        self.col_positions = self.compute_positions(
            GRID_COLS,
            left=SCREEN_MARGIN,
            right=self.window_width - SIDEBAR_WIDTH - SCREEN_MARGIN
        )

        self.row_positions = self.compute_positions(
            GRID_ROWS,
            top=SCREEN_MARGIN,
            bottom=self.window_height - SCREEN_MARGIN
        )

        self.cars = []
        self.spawn_timer = 0.0
        self.spawn_interval = 0.5 if headless else 1

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
                self.road_speed_limits["horizontal"][(row, col)] = 1.0
        for row in range(GRID_ROWS - 1):
            for col in range(GRID_COLS):
                self.road_speed_limits["vertical"][(row, col)] = 0.5

        self.intersections = []
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                cx = self.col_positions[col]
                cy = self.row_positions[row]
                inter = Intersection(col, row, cx, cy, GRID_ROWS, GRID_COLS)
                inter.waiting_cars = 0
                inter.waiting_time_total = 0.0
                inter.prev_waiting_cars = 0
                inter.prev_waiting_time = 0.0
                inter.congestion_heat = 0.0
                self.intersections.append(inter)

    def compute_positions(self, count, left=None, right=None, top=None, bottom=None):
        if left is not None and right is not None:
            spacing = (right - left) / (count - 1)
            return [left + i * spacing for i in range(count)]
        elif top is not None and bottom is not None:
            spacing = (bottom - top) / (count - 1)
            return [top + i * spacing for i in range(count)]
        else:
            raise ValueError("Must specify left/right or top/bottom bounds.")

    def get_speed_limit(self, car):
        if car.direction in ("E", "W"):
            row = min(range(GRID_ROWS), key=lambda r: abs(car.y - self.row_positions[r]))
            col = max(0, min(GRID_COLS - 2, sum(car.x > cp for cp in self.col_positions) - 1))
            return self.road_speed_limits["horizontal"].get((row, col), 1.0)
        else:
            col = min(range(GRID_COLS), key=lambda c: abs(car.x - self.col_positions[c]))
            row = max(0, min(GRID_ROWS - 2, sum(car.y > rp for rp in self.row_positions) - 1))
            return self.road_speed_limits["vertical"].get((row, col), 1.0)

    def draw(self, screen, dt, show_heatmap=True):
        for cy in self.row_positions:
            pygame.draw.rect(screen, (100, 100, 100), (
                self.col_positions[0],
                cy - ROAD_WIDTH // 2,
                self.col_positions[-1] - self.col_positions[0],
                ROAD_WIDTH
            ))

        for cx in self.col_positions:
            pygame.draw.rect(screen, (100, 100, 100), (
                cx - ROAD_WIDTH // 2,
                self.row_positions[0],
                ROAD_WIDTH,
                self.row_positions[-1] - self.row_positions[0]
            ))

        for inter in self.intersections:
            inter.update(dt)
            inter.draw(screen)

        for car in self.cars:
            car.road_speed_factor = self.get_speed_limit(car)
            car.update(self.intersections, dt, self.cars)
            car.draw(screen)
            nearest = car.get_nearest_intersection(self.intersections)
            if car.state == "waiting" and nearest:
                nearest.waiting_cars += 1
                nearest.waiting_time_total += dt

        for inter in self.intersections:
            congestion_signal = inter.waiting_cars + inter.waiting_time_total
            inter.congestion_heat = max(0.0, inter.congestion_heat * 0.58 + congestion_signal * dt * 2)

            if inter.congestion_heat > 2.0:
                intensity = min(150, int(inter.congestion_heat * 10))
                glow_surface = pygame.Surface((ROAD_WIDTH * 2, ROAD_WIDTH * 2), pygame.SRCALPHA)
                if show_heatmap:
                    pygame.draw.circle(glow_surface, (255, 0, 0, intensity), (ROAD_WIDTH, ROAD_WIDTH), ROAD_WIDTH)
                    screen.blit(glow_surface, (inter.cx - ROAD_WIDTH, inter.cy - ROAD_WIDTH))

        for inter in self.intersections:
            inter.prev_waiting_cars = inter.waiting_cars
            inter.prev_waiting_time = inter.waiting_time_total
            inter.waiting_cars = 0
            inter.waiting_time_total = 0.0

        remaining = []
        for c in self.cars:
            if -50 <= c.x <= self.window_width - SIDEBAR_WIDTH + 50 and -50 <= c.y <= self.window_height + 50:
                remaining.append(c)
            else:
                self.total_wait_time += c.stopped_time
                self.cars_processed += 1
        self.cars = remaining

        self.avg_wait_time = self.total_wait_time / self.cars_processed if self.cars_processed > 0 else 0.0

        self.spawn_timer += dt
        if self.headless:
            while self.spawn_timer >= self.spawn_interval:
                self.spawn_car()
                self.spawn_timer -= self.spawn_interval
        else:
            if self.spawn_timer >= self.spawn_interval:
                self.spawn_car()
                self.spawn_timer = 0

        mildly_stopped = sum(1 for c in self.cars if c.stopped_time > 10.0)
        severely_stopped = sum(1 for c in self.cars if c.stopped_time > 20.0)
        queued = len(self.cars)
        intersection_congestion = sum(i.prev_waiting_cars for i in self.intersections)
        intersection_wait_penalty = sum(i.prev_waiting_time for i in self.intersections)
        heavy_congestion_penalty = max(0, queued - HEAVY_CONGESTION_THRESHOLD)

        car_weight = 0.05
        time_weight = 0.02
        norm_waiting_cars = sum(i.prev_waiting_cars * car_weight for i in self.intersections)
        norm_waiting_time = sum(i.prev_waiting_time * time_weight for i in self.intersections)
        avg_age = sum(c.age for c in self.cars) / len(self.cars) if self.cars else 0
        spillovers = sum(1 for i in self.intersections if i.prev_waiting_cars > SPILLOVER_THRESHOLD)
        low_throughput_penalty = 0.0
        if self.cars_processed < 10:
            low_throughput_penalty = 5.0

        self.fitness = (
            0.4 * self.avg_wait_time +
            1.0 * mildly_stopped +
            3.0 * severely_stopped +
            0.15 * heavy_congestion_penalty +
            0.05 * intersection_congestion +
            0.02 * intersection_wait_penalty +
            norm_waiting_cars +
            norm_waiting_time -
            0.05 * self.cars_processed + 
            0.1 * avg_age +
            0.3 * spillovers +
            low_throughput_penalty
        )
        self.total_congestion = intersection_congestion

    def spawn_car(self):
        edge = random.choices(["N", "S", "E", "W"], weights=[1, 1, 3, 3])[0]

        if edge == "N":
            col = random.choice(self.col_positions)
            x, y, d = col, self.window_height, "N"
        elif edge == "S":
            col = random.choice(self.col_positions)
            x, y, d = col, 0, "S"
        elif edge == "E":
            row = random.choice(self.row_positions)
            x, y, d = 0, row, "E"
        elif edge == "W":
            row = random.choice(self.row_positions)
            x, y, d = self.window_width - SIDEBAR_WIDTH, row, "W"

        self.cars.append(Car(x, y, d, max_speed=CAR_SPEED, acceleration=CAR_ACCEL))
