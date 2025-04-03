import pygame
import sys
from simulation.grid import Grid
from optimizer.controller import AnnealingController

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 1000

BG_COLOR = (30, 30, 30)
TEXT_COLOR = (255, 255, 255)

SIDEBAR_WIDTH = 200
SIDEBAR_PADDING = 10
GRAPH_HEIGHT = 100
GRAPH_WIDTH = 180




SIM_SPEED = 1.0  # default time scale

def draw_ui(screen, font, grid, controller):
    debug = controller.get_debug_info()

    # Fonts
    header_font = pygame.font.SysFont("Arial", 20, bold=True)
    small_font = pygame.font.SysFont("Arial", 16)
    screen_width = screen.get_width()


    # Sidebar background
    pygame.draw.rect(screen, (50, 50, 50), (screen_width - SIDEBAR_WIDTH, 0, SIDEBAR_WIDTH, screen.get_height()))

    draw_x = screen_width - SIDEBAR_WIDTH + SIDEBAR_PADDING
    max_text_width = SIDEBAR_WIDTH - 2 * SIDEBAR_PADDING

    # Color-coded status
    status = debug["status"]
    if "Evaluating" in status:
        status_color = (255, 215, 0)  # yellow
    elif "Applying" in status:
        status_color = (100, 255, 100)  # green
    else:
        status_color = TEXT_COLOR

    lines = [
        (header_font, "Live Traffic Stats:", TEXT_COLOR),
        (small_font, f"Avg Wait: {grid.avg_wait_time:.1f}s", TEXT_COLOR),
        (small_font, f"Cars Processed: {grid.cars_processed}", TEXT_COLOR),
        (small_font, f"Live Fitness: {grid.fitness:.2f}", TEXT_COLOR),
        (header_font, "", TEXT_COLOR),
        (header_font, "Annealing Debug:", TEXT_COLOR),
        (small_font, f"Best Fitness: {debug['best_fitness']:.2f}", TEXT_COLOR),
        (small_font, f"Current Fitness: {debug['current_fitness']:.2f}", TEXT_COLOR),
        (small_font, f"Temp: {debug['temperature']:.2f}", TEXT_COLOR),
        (small_font, f"Last Sim Cars: {debug['cars_processed']}", TEXT_COLOR),
        (small_font, f"Max Sim Cars: {debug['max_cars']}", TEXT_COLOR),
        (small_font, f"Next Mutation: {debug['countdown']:.1f}s", TEXT_COLOR),
        (small_font, "Status:", TEXT_COLOR),
        (small_font, status, status_color),
        (small_font, "", TEXT_COLOR),
        (small_font, f"Sim Speed: {SIM_SPEED:.1f}x", TEXT_COLOR),
        (small_font, "", TEXT_COLOR),
        (header_font, "Fitness Trend", TEXT_COLOR),
    ]

    y = 20
    for font_type, text, color in lines:
        label_surface = font_type.render(text, True, color)
        if label_surface.get_width() > max_text_width:
            # Truncate text if needed
            max_chars = int(len(text) * max_text_width / label_surface.get_width()) - 3
            text = text[:max_chars] + "..."
            label_surface = font_type.render(text, True, color)

        screen.blit(label_surface, (draw_x, y))
        y += font_type.get_linesize() + 4

    # Fitness graph
    points = debug.get("fitness_history", [])
    graph_surface = pygame.Surface((GRAPH_WIDTH, GRAPH_HEIGHT))
    graph_surface.fill((20, 20, 20))

    if len(points) > 1:
        max_val = max(points)
        min_val = min(points)
        range_val = max(max_val - min_val, 0.05)

        for i in range(len(points) - 1):
            x1 = i * GRAPH_WIDTH // (len(points) - 1)
            x2 = (i + 1) * GRAPH_WIDTH // (len(points) - 1)

            y1 = GRAPH_HEIGHT - int((points[i] - min_val) / range_val * GRAPH_HEIGHT)
            y2 = GRAPH_HEIGHT - int((points[i + 1] - min_val) / range_val * GRAPH_HEIGHT)

            pygame.draw.line(graph_surface, (0, 255, 0), (x1, y1), (x2, y2), 2)
            pygame.draw.circle(graph_surface, (0, 255, 0), (x1, y1), 2)

        last_y = GRAPH_HEIGHT - int((points[-1] - min_val) / range_val * GRAPH_HEIGHT)
        pygame.draw.circle(graph_surface, (0, 255, 0), (GRAPH_WIDTH - 2, last_y), 2)
    else:
        placeholder_font = pygame.font.SysFont("Arial", 14)
        msg = placeholder_font.render("Waiting for data...", True, (150, 150, 150))
        graph_surface.blit(msg, (10, GRAPH_HEIGHT // 2 - msg.get_height() // 2))

    screen.blit(graph_surface, (draw_x, y))



def main():

    notification_text = ""
    notification_timer = 0.0
    global SIM_SPEED  # make speed adjustable
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
        dt *= SIM_SPEED  # Apply time scaling

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_EQUALS, pygame.K_PLUS):
                    SIM_SPEED = min(5.0, SIM_SPEED + 0.5)
                elif event.key == pygame.K_MINUS:
                    SIM_SPEED = max(0.5, SIM_SPEED - 0.5)

        # Show notification if a new best config was applied
        if controller.status_message == controller.STATUS_BEST_APPLIED:
            if notification_timer <= 0:  # Only trigger once
                print(f"Notification: {controller.status_message}")
                notification_text = controller.status_message
                notification_timer = 2.5  # show for 2.5 seconds
                controller.status_message = controller.STATUS_WAITING

        controller.update(dt, grid)



        screen.fill(BG_COLOR)
        grid.draw(screen, dt)
        draw_ui(screen, font, grid, controller)
        if notification_timer > 0:
            print(f"Notification: {notification_text}")
            notification_timer -= dt
            alpha = int(255 * min(1.0, notification_timer / 0.5)) if notification_timer < 0.5 else 255
            notif_surface = pygame.Surface((500, 50), pygame.SRCALPHA)
            notif_surface.fill((0, 0, 0, 180))
            font_big = pygame.font.SysFont("Arial", 24, bold=True)
            text = font_big.render(notification_text, True, (255, 255, 255))
            notif_surface.blit(text, (250 - text.get_width() // 2, 10))
            notif_surface.set_alpha(alpha)
            sim_width = WINDOW_WIDTH - SIDEBAR_WIDTH
            text_rect = notif_surface.get_rect(center=(sim_width // 2, WINDOW_HEIGHT // 2))
            screen.blit(notif_surface, text_rect)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
