import pygame

CAR_WIDTH = 12
CAR_LENGTH = 20
CAR_COLOR = (0, 200, 255)

class Car:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction  # "N", "S", "E", "W"
        self.speed = 2

    def update(self):
        if self.direction == "N":
            self.y -= self.speed
        elif self.direction == "S":
            self.y += self.speed
        elif self.direction == "E":
            self.x += self.speed
        elif self.direction == "W":
            self.x -= self.speed

    def draw(self, screen):
        if self.direction in ("N", "S"):
            rect = pygame.Rect(self.x - CAR_WIDTH // 2, self.y - CAR_LENGTH // 2, CAR_WIDTH, CAR_LENGTH)
        else:
            rect = pygame.Rect(self.x - CAR_LENGTH // 2, self.y - CAR_WIDTH // 2, CAR_LENGTH, CAR_WIDTH)

        pygame.draw.rect(screen, CAR_COLOR, rect)
