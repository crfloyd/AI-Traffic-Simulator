import pygame
import random
from simulation.grid import Grid

class Simulator:
    def __init__(self):
        pygame.init()
        self.screen = pygame.Surface((800, 800))  # offscreen surface for headless sim
        self.clock = pygame.time.Clock()

    def run(self, config, duration=30, return_cars=False):
        grid = Grid(headless=True)

        # Apply config to each intersection
        for inter, cfg in zip(grid.intersections, config):
            inter.ns_duration = cfg["ns_duration"]
            inter.ew_duration = cfg["ew_duration"]
            inter.elapsed = random.uniform(0, 3)  # Desync light timers

        warmup = 5.0  # Let traffic settle
        total_sim_time = duration + warmup

        # Fixed timestep (simulate at 60 FPS)
        dt = 1.0 / 60.0
        steps = int(total_sim_time / dt)

        for _ in range(steps):
            grid.draw(self.screen, dt)

        # Only count stats from final `duration` seconds
        if return_cars:
            return grid.fitness, (grid.cars_processed / duration) * 60, grid.cars_processed
        else:
            return grid.fitness, (grid.cars_processed / duration) * 60




