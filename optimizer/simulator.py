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
        for inter, cfg in zip(grid.intersections, config):
            inter.ns_duration = cfg["ns_duration"]
            inter.ew_duration = cfg["ew_duration"]
            inter.all_red_duration = cfg["all_red_duration"]



        elapsed = 0.0
        while elapsed < duration:
            dt = self.clock.tick(60) / 1000.0
            elapsed += dt

            # Run one simulation step
            grid.draw(self.screen, dt)

        return grid.fitness
