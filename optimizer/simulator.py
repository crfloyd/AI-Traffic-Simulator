import pygame
import random
from simulation.grid import Grid

class Simulator:
    def __init__(self):
        pygame.init()
        self.screen = pygame.Surface((800, 800))  # offscreen surface for headless sim
        self.clock = pygame.time.Clock()

    def run(self, config, duration=30, return_cars=False):
        grid = Grid(headless=True)  # ✅ use headless mode for sim
        
        for inter in grid.intersections:
            print(f"({inter.grid_x}, {inter.grid_y}) phase={inter.phase} elapsed={inter.elapsed:.2f}")
        print(f"Cars processed: {grid.cars_processed}, Still on grid: {len(grid.cars)}")

        # Apply config to each intersection
        for inter, cfg in zip(grid.intersections, config):
            inter.ns_duration = cfg["ns_duration"]
            inter.ew_duration = cfg["ew_duration"]
            inter.elapsed = random.uniform(0, 3)

        warmup = 10
        sim_time = duration
        elapsed = 0.0

        while elapsed < warmup + sim_time:
            dt = self.clock.tick(60) / 1000.0
            elapsed += dt
            grid.draw(self.screen, dt)

        throughput = (grid.cars_processed / duration) * 60

        if return_cars:
            return grid.fitness, throughput, grid.cars_processed
        else:
            return grid.fitness, throughput



