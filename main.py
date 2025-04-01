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
GRAPH_HEIGHT = 100
GRAPH_WIDTH = 180


SIM_SPEED = 1.0  # default time scale

def draw_ui(screen, font, grid, controller):
    debug = controller.get_debug_info()

    # Sidebar
    pygame.draw.rect(screen, (50, 50, 50), (WINDOW_WIDTH - SIDEBAR_WIDTH, 0, SIDEBAR_WIDTH, WINDOW_HEIGHT))
    draw_x = WINDOW_WIDTH - SIDEBAR_WIDTH + SIDEBAR_PADDING

    metrics = [
        "Live Traffic Stats:",
        f"  Avg Wait: {grid.avg_wait_time:.1f}s",
        f"  Cars Processed: {grid.cars_processed}",
        f"  Live Fitness: {grid.fitness:.2f}",
        # f"  Throughput: {debug['throughput']:.1f}/min",
        "",
        "Annealing Debug:",
        f"  Best Fitness: {debug['best_fitness']:.2f}",
        f"  Temp: {debug['temperature']:.2f}",
        f"  Next Mutation: {debug['countdown']:.1f}s",
        "",
        f"Sim Speed: {SIM_SPEED:.1f}x"
    ]

    for idx, text in enumerate(metrics):
        label = font.render(text, True, TEXT_COLOR)
        screen.blit(label, (draw_x, 20 + idx * 30))

    # === Fitness Graph ===
    graph_top = 420
    max_points = 100  # fixed width window
    points = debug.get("fitness_history", [])
    padded_points = points[-max_points:]  # ensure it's capped at max

    # If no values yet, fill with None (to still show graph base)
    if len(padded_points) < max_points:
        padded_points = [None] * (max_points - len(padded_points)) + padded_points

    min_val = min((v for v in padded_points if v is not None), default=0)
    max_val = max((v for v in padded_points if v is not None), default=1)
    range_val = max_val - min_val or 1

    # Graph surface
    graph_surface = pygame.Surface((GRAPH_WIDTH, GRAPH_HEIGHT))
    graph_surface.fill((20, 20, 20))

    # Draw line and points
    last_pos = None
    for i, val in enumerate(padded_points):
        x = int(i * (GRAPH_WIDTH / max_points))
        if val is not None:
            y = GRAPH_HEIGHT - int((val - min_val) / range_val * GRAPH_HEIGHT)

            # Line
            if last_pos:
                pygame.draw.line(graph_surface, (0, 255, 0), last_pos, (x, y), 2)
            last_pos = (x, y)

            # Dot
            pygame.draw.circle(graph_surface, (255, 255, 255), (x, y), 2)
        else:
            last_pos = None  # break line

    # Blit graph
    screen.blit(graph_surface, (draw_x, graph_top))

    # Min/max labels
    min_label = font.render(f"{min_val:.2f}", True, TEXT_COLOR)
    max_label = font.render(f"{max_val:.2f}", True, TEXT_COLOR)
    screen.blit(min_label, (draw_x, graph_top + GRAPH_HEIGHT - 20))
    screen.blit(max_label, (draw_x, graph_top - 20))

    # Step label
    step_label = font.render(f"Step: {len(points)}", True, TEXT_COLOR)
    screen.blit(step_label, (draw_x, graph_top + GRAPH_HEIGHT + 10))

    # Graph title
    label = font.render("Fitness Trend", True, TEXT_COLOR)
    screen.blit(label, (draw_x, graph_top - 40))




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
