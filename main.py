import pygame
import sys
from simulation.grid import Grid
from optimizer.controller import AnnealingController

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 1000

BG_COLOR = (30, 30, 30)
TEXT_COLOR = (255, 255, 255)
COLOR_GREEN = (10, 255, 0)

SIDEBAR_WIDTH = 200
SIDEBAR_PADDING = 10
GRAPH_HEIGHT = 100
GRAPH_WIDTH = 180

HEATMAP_TOGGLE_RECT = pygame.Rect(WINDOW_WIDTH - SIDEBAR_WIDTH + 10, 590, 180, 50)
PAUSE_BUTTON_RECT = pygame.Rect(WINDOW_WIDTH - SIDEBAR_WIDTH + 10, WINDOW_HEIGHT - 50, 180, 30)

SIM_SPEED = 1.0  # default time scale
SIM_SPEED_SECTION_TOP = 370
SIM_SPEED_SECTION_HEIGHT = 60
SPEED_DOWN_RECT = pygame.Rect(WINDOW_WIDTH - SIDEBAR_WIDTH + 10, SIM_SPEED_SECTION_TOP + 25, 30, 30)
SPEED_UP_RECT = pygame.Rect(WINDOW_WIDTH - SIDEBAR_WIDTH + 160, SIM_SPEED_SECTION_TOP + 25, 30, 30)


def draw_ui(screen, font, grid, controller, show_heatmap, paused, fps):
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
    elif "Better" in status:
        status_color = (100, 255, 100)  # green
    elif "Optimization complete" in status:
        status_color = (50, 245, 50)  # green
    else:
        status_color = TEXT_COLOR

    # --- Sim Speed Section Box ---
    pygame.draw.rect(screen, (40, 40, 40), (screen_width - SIDEBAR_WIDTH + 5, SIM_SPEED_SECTION_TOP, 190, SIM_SPEED_SECTION_HEIGHT), border_radius=8)

    # Draw "Sim Speed:" centered at the top of the box
    speed_label_font = pygame.font.SysFont("Arial", 15)
    speed_title = speed_label_font.render("Sim Speed:", True, TEXT_COLOR)
    speed_title_rect = speed_title.get_rect(center=(screen_width - SIDEBAR_WIDTH + SIDEBAR_WIDTH // 2, SIM_SPEED_SECTION_TOP + 12))
    screen.blit(speed_title, speed_title_rect)

    # Speed buttons
    pygame.draw.rect(screen, (180, 180, 180), SPEED_DOWN_RECT, border_radius=4)
    pygame.draw.rect(screen, (180, 180, 180), SPEED_UP_RECT, border_radius=4)

    arrow_font = pygame.font.SysFont("Arial", 20, bold=True)
    minus_surface = arrow_font.render("<", True, (0, 0, 0))
    plus_surface = arrow_font.render(">", True, (0, 0, 0))
    screen.blit(minus_surface, minus_surface.get_rect(center=SPEED_DOWN_RECT.center))
    screen.blit(plus_surface, plus_surface.get_rect(center=SPEED_UP_RECT.center))

    # Speed value centered between buttons
    speed_value_font = pygame.font.SysFont("Arial", 16, bold=True)
    value_label = speed_value_font.render(f"{SIM_SPEED:.1f}x", True, TEXT_COLOR)
    value_rect = value_label.get_rect(center=(screen_width - SIDEBAR_WIDTH + 100, SPEED_DOWN_RECT.centery))
    screen.blit(value_label, value_rect)

    # Dynamic color for temperature (hot → cold)
    T = debug['temperature']
    T_min = 1
    T_max = 150
    alpha = max(0.0, min(1.0, (T - T_min) / (T_max - T_min)))  # 1.0 = hot, 0.0 = cold

    # Interpolate from red (255, 50, 50) to blue (80, 150, 255)
    r = int(255 * alpha + 80 * (1 - alpha))
    g = int(50 * alpha + 150 * (1 - alpha))
    b = int(50 * alpha + 255 * (1 - alpha))
    temp_color = (r, g, b)
    
    lines = [
        (header_font, "Live Traffic Stats:", TEXT_COLOR),
        (small_font, f"FPS: {fps:.1f}", TEXT_COLOR),
        (small_font, f"Avg Wait: {grid.avg_wait_time:.1f}s", TEXT_COLOR),
        (small_font, f"Cars in grid: {debug['cars_in_grid']:.2f}", TEXT_COLOR),
        
        (header_font, "", TEXT_COLOR),
        (header_font, "Annealing Debug:", TEXT_COLOR),
        (small_font, f"Best Fitness: {debug['best_fitness']:.2f}", TEXT_COLOR),
        (small_font, f"Last Fitness: {debug['current_fitness']:.2f}", TEXT_COLOR),
        (small_font, f"Temp: {debug['temperature']:.2f}", temp_color),
        (small_font, f"Last Sim Cars: {debug['cars_processed']}", TEXT_COLOR),
        (small_font, f"Max Sim Cars: {debug['max_cars']}", TEXT_COLOR),
        (small_font, f"Next Mutation: {debug['countdown']:.1f}s", TEXT_COLOR),
        (small_font, "Status:", TEXT_COLOR),
        (small_font, status, status_color),
        (small_font, "", TEXT_COLOR),
        (small_font, "", TEXT_COLOR),
        (small_font, "", TEXT_COLOR),
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


    # Draw the heatmap toggle button
    checkbox_label = "Show Heatmap"
    checkbox_font = pygame.font.SysFont("Arial", 16)
    checkbox_surface = checkbox_font.render(checkbox_label, True, TEXT_COLOR)
    screen.blit(checkbox_surface, (HEATMAP_TOGGLE_RECT.x, HEATMAP_TOGGLE_RECT.y))

    box_size = 20
    box_rect = pygame.Rect(HEATMAP_TOGGLE_RECT.x + 130, HEATMAP_TOGGLE_RECT.y, box_size, box_size)
    pygame.draw.rect(screen, (200, 200, 200), box_rect)
    if show_heatmap:
        # Draw a black checkmark
        pygame.draw.line(screen, (0, 0, 0), (box_rect.left + 4, box_rect.centery),
                            (box_rect.centerx - 2, box_rect.bottom - 4), 2)
        pygame.draw.line(screen, (0, 0, 0), (box_rect.centerx - 2, box_rect.bottom - 4),
                            (box_rect.right - 4, box_rect.top + 4), 2)
        
    



    # Draw Start/Pause button
    if paused:
        pause_color = (220, 100, 100)  # light red
        pause_label = "Paused"
    else:
        pause_color = (100, 220, 100)  # light green
        pause_label = "Running"

    pygame.draw.rect(screen, pause_color, PAUSE_BUTTON_RECT, border_radius=6)

    pause_font = pygame.font.SysFont("Arial", 16, bold=True)
    pause_surface = pause_font.render(pause_label, True, (0, 0, 0))
    pause_rect = pause_surface.get_rect(center=PAUSE_BUTTON_RECT.center)
    screen.blit(pause_surface, pause_rect)





def main():
    global SIM_SPEED
    paused = True 
    notification_text = ""
    notification_timer = 0.0
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Traffic Flow Optimization")
    show_heatmap = False

    font = pygame.font.SysFont("Arial", 20)
    grid = Grid()
    controller = AnnealingController(grid=grid)
    clock = pygame.time.Clock()
    running = True
    last_status_message = None

    PAUSE_BUTTON_RECT.y = screen.get_height() - 80
    while running:
        dt = clock.tick(60) / 1000.0 
        fps = clock.get_fps()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_EQUALS, pygame.K_PLUS):
                    SIM_SPEED = min(10.0, SIM_SPEED + 0.5)
                elif event.key == pygame.K_MINUS:
                    SIM_SPEED = max(0.5, SIM_SPEED - 0.5)
                elif event.key == pygame.K_h:
                    show_heatmap = not show_heatmap
                elif event.key == pygame.K_SPACE:
                    paused = not paused
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                box_click_rect = pygame.Rect(HEATMAP_TOGGLE_RECT.x + 130, HEATMAP_TOGGLE_RECT.y, 20, 20)
                if box_click_rect.collidepoint(event.pos):
                    show_heatmap = not show_heatmap
                if PAUSE_BUTTON_RECT.collidepoint(event.pos):
                    paused = not paused
                if SPEED_DOWN_RECT.collidepoint(event.pos):
                    SIM_SPEED = max(0.5, SIM_SPEED - 0.5)
                elif SPEED_UP_RECT.collidepoint(event.pos):
                    SIM_SPEED = min(10.0, SIM_SPEED + 0.5)



        # Show notification if a new best config was applied
        if controller.status_message != last_status_message:
            if controller.status_message == controller.STATUS_BEST_APPLIED:
                print(f"Notification: {controller.status_message}")
                notification_text = controller.status_message
                notification_timer = 2.5
            last_status_message = controller.status_message

        if not paused:
            controller.update(dt * SIM_SPEED)


        screen.fill(BG_COLOR)
        
        scaled_dt = 0 if paused else dt * SIM_SPEED
        real_dt = 0 if paused else dt

        grid.draw(screen, scaled_dt, show_heatmap=show_heatmap, real_dt=real_dt)

        draw_ui(screen, font, grid, controller, show_heatmap, paused, fps)

        sim_width = WINDOW_WIDTH - SIDEBAR_WIDTH
        text_rect = pygame.Rect(0, 0, 500, 50)
        text_rect.center = (sim_width // 2, WINDOW_HEIGHT // 2)

        # "Better Config" notification
        if notification_timer > 0:
            notification_timer -= dt
            alpha = int(255 * min(1.0, notification_timer / 0.5)) if notification_timer < 0.5 else 255
            notif_surface = pygame.Surface((500, 50), pygame.SRCALPHA)
            notif_surface.fill((0, 0, 0, 180))
            font_big = pygame.font.SysFont("Arial", 24, bold=True)
            text = font_big.render(notification_text, True, (255, 255, 255))
            notif_surface.blit(text, (250 - text.get_width() // 2, 10))
            notif_surface.set_alpha(alpha)
            screen.blit(notif_surface, text_rect)

        # "Paused" overlay
        if paused:
            pause_overlay = pygame.Surface((500, 50), pygame.SRCALPHA)
            pause_overlay.fill((0, 0, 0, 180))
            pause_font = pygame.font.SysFont("Arial", 24, bold=True)
            pause_text = pause_font.render("⏸ Paused", True, (255, 255, 255))
            pause_overlay.blit(pause_text, (250 - pause_text.get_width() // 2, 10))
            pause_overlay.set_alpha(200)
            screen.blit(pause_overlay, text_rect)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
