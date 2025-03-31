import pygame
from simulation.grid import Grid

class Simulator:
    def __init__(self):
        pygame.init()
        self.screen = pygame.Surface((800, 800))  # offscreen surface for headless sim
        self.clock = pygame.time.Clock()

    def run(self, config, duration=30):
        grid = Grid()

        # Apply config (light durations)
        for inter in grid.intersections:
            inter.ns_duration = config.get("ns_duration", 5)
            inter.ew_duration = config.get("ew_duration", 5)
            inter.all_red_duration = config.get("all_red_duration", 2)

        elapsed = 0.0
        while elapsed < duration:
            dt = self.clock.tick(60) / 1000.0
            elapsed += dt

            # Run one simulation step
            grid.draw(self.screen, dt)

        return grid.fitness
