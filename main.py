import pygame
import sys
from simulation.grid import Grid
from optimizer.controller import AnnealingController



WINDOW_WIDTH = 800
WINDOW_HEIGHT = 800
BG_COLOR = (30, 30, 30)
TEXT_COLOR = (255, 255, 255)

def draw_ui(screen, font, grid, controller):
    # Example placeholder UI panel
    pygame.draw.rect(screen, (50, 50, 50), (600, 0, 200, WINDOW_HEIGHT))  # Sidebar
    debug = controller.get_debug_info()

    metrics = [
        "Live Traffic Stats:",
        f"  Avg Wait: {grid.avg_wait_time:.1f}s",
        f"  Cars Processed: {grid.cars_processed}",
        f"  Live Fitness: {grid.fitness:.2f}",
        "",
        "Annealing Debug:",
        f"  Best Fitness: {debug['best_fitness']:.2f}",
        f"  Temp: {debug['temperature']:.2f}",
        f"  Next Mutation: {debug['countdown']:.1f}s"
    ]


    for idx, text in enumerate(metrics):
        label = font.render(text, True, TEXT_COLOR)
        screen.blit(label, (610, 20 + idx * 30))

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Traffic Flow Optimization")
    clock = pygame.time.Clock()

    font = pygame.font.SysFont("Arial", 20)
    grid = Grid()
    controller = AnnealingController()

    running = True

    while running:
        dt = clock.tick(60) / 1000.0  # Delta time in seconds

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(BG_COLOR)
        controller.update(dt, grid)
        grid.draw(screen, dt)
        draw_ui(screen, font, grid, controller)
        pygame.display.flip()


    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

