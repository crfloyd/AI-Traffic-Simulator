import pygame
import sys
from simulation.grid import Grid


WINDOW_WIDTH = 800
WINDOW_HEIGHT = 800
BG_COLOR = (30, 30, 30)
TEXT_COLOR = (255, 255, 255)

def draw_ui(screen, font):
    # Example placeholder UI panel
    pygame.draw.rect(screen, (50, 50, 50), (600, 0, 200, WINDOW_HEIGHT))  # Sidebar
    metrics = [
        "Avg Wait: 0.0s",
        "Cars Processed: 0",
        "Fitness: 0.0",
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

    running = True

    while running:
        screen.fill(BG_COLOR)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        grid.draw(screen)
        draw_ui(screen, font)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
