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
        self.state = "moving"  # or "waiting"
        self.stopped_time = 0.0

    def update(self, intersections, dt):
        for inter in intersections:
            if self.is_near(inter):
                if not self.can_go(inter):
                    self.state = "waiting"
                    self.stopped_time += dt
                    return  # stop moving

        self.state = "moving"
        self.stopped_time = 0

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
        
    
    def is_near(self, intersection, threshold=20):
        if self.direction == "N":
            return abs(self.x - intersection.cx) < 10 and 0 < self.y - intersection.cy < threshold
        if self.direction == "S":
            return abs(self.x - intersection.cx) < 10 and 0 < intersection.cy - self.y < threshold
        if self.direction == "E":
            return abs(self.y - intersection.cy) < 10 and 0 < intersection.cx - self.x < threshold
        if self.direction == "W":
            return abs(self.y - intersection.cy) < 10 and 0 < self.x - intersection.cx < threshold
        return False
    
    def can_go(self, intersection):
        if intersection.phase == "ALL_RED":
            return False
        if self.direction in ("N", "S") and intersection.phase == "NS":
            return True
        if self.direction in ("E", "W") and intersection.phase == "EW":
            return True
        return False


