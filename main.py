import pygame
import sys
from simulation.grid import Grid
from optimizer.controller import AnnealingController

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 800
BG_COLOR = (30, 30, 30)
TEXT_COLOR = (255, 255, 255)

SIDEBAR_WIDTH = 200
SIDEBAR_PADDING = 10

SIM_SPEED = 1.0  # default time scale

def draw_ui(screen, font, grid, controller):
    debug = controller.get_debug_info()

    # Draw sidebar with padding
    pygame.draw.rect(screen, (50, 50, 50), (WINDOW_WIDTH - SIDEBAR_WIDTH, 0, SIDEBAR_WIDTH, WINDOW_HEIGHT))

    metrics = [
        "Live Traffic Stats:",
        f"  Avg Wait: {grid.avg_wait_time:.1f}s",
        f"  Cars Processed: {grid.cars_processed}",
        f"  Live Fitness: {grid.fitness:.2f}",
        "",
        "Annealing Debug:",
        f"  Best Fitness: {debug['best_fitness']:.2f}",
        f"  Temp: {debug['temperature']:.2f}",
        f"  Next Mutation: {debug['countdown']:.1f}s",
        "",
        f"Sim Speed: {SIM_SPEED:.1f}x"
    ]

    draw_x = WINDOW_WIDTH - SIDEBAR_WIDTH + SIDEBAR_PADDING

    for idx, text in enumerate(metrics):
        label = font.render(text, True, TEXT_COLOR)
        screen.blit(label, (draw_x, 20 + idx * 30))

def main():
    global SIM_SPEED  # make speed adjustable
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Traffic Flow Optimization")
    clock = pygame.time.Clock()

    font = pygame.font.SysFont("Arial", 20)
    grid = Grid()

    initial_config = [
        {"ns_duration": 5, "ew_duration": 5, "all_red_duration": 2}
        for _ in range(9)
    ]
    controller = AnnealingController()

    running = True

    while running:
        dt = clock.tick(60) / 1000.0  # Delta time in seconds
        dt *= SIM_SPEED  # Apply time scaling

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_EQUALS, pygame.K_PLUS):
                    SIM_SPEED = min(5.0, SIM_SPEED + 0.5)
                elif event.key == pygame.K_MINUS:
                    SIM_SPEED = max(0.5, SIM_SPEED - 0.5)
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_EQUALS, pygame.K_PLUS, pygame.K_KP_PLUS):
                    SIM_SPEED = min(5.0, SIM_SPEED + 0.5)
                    print(f"Speed increased: {SIM_SPEED:.1f}x")
                elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    SIM_SPEED = max(0.5, SIM_SPEED - 0.5)
                    print(f"Speed decreased: {SIM_SPEED:.1f}x")


        controller.update(dt, grid)

        screen.fill(BG_COLOR)
        grid.draw(screen, dt)
        draw_ui(screen, font, grid, controller)
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
