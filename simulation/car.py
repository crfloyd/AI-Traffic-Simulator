import pygame
import math

CAR_WIDTH = 12
CAR_LENGTH = 20
CAR_COLOR = (0, 200, 255)
CAR_STOP_GAP = 15
CAR_START_GAP = 35

class Car:
    def __init__(self, x, y, direction, max_speed=100, acceleration=50, initial_speed=None):
        self.x = x
        self.y = y
        self.direction = direction  # "N", "S", "E", "W"
        self.velocity = 0.0
        self.max_speed = max_speed
        self.speed = initial_speed if initial_speed is not None else 0.0
        self.acceleration = acceleration
        self.state = "moving"  # or "waiting"
        self.stopped_time = 0.0
        self.length = CAR_LENGTH
        self.width = CAR_WIDTH


    def update(self, intersections, dt, cars):
        near_intersection = any(self.is_near(inter) and not self.can_go(inter) for inter in intersections)

        if near_intersection or self.car_blocking_ahead(cars):
            # Stop if there's a red light or car blocking
            self.velocity = 0.0
            self.state = "waiting"
            self.stopped_time += dt
            return
        else:
            # Accelerate
            target_speed = self.max_speed * getattr(self, 'road_speed_factor', 1.0)
            self.velocity += self.acceleration * dt
            self.velocity = min(self.velocity, target_speed)

            self.state = "moving"
            self.stopped_time = 0.0

        dist = self.velocity * dt
        if self.direction == "N":
            self.y -= dist
        elif self.direction == "S":
            self.y += dist
        elif self.direction == "E":
            self.x += dist
        elif self.direction == "W":
            self.x -= dist

    def draw(self, screen):
        if self.direction in ("N", "S"):
            rect = pygame.Rect(self.x - CAR_WIDTH // 2, self.y - CAR_LENGTH // 2, CAR_WIDTH, CAR_LENGTH)
        else:
            rect = pygame.Rect(self.x - CAR_LENGTH // 2, self.y - CAR_WIDTH // 2, CAR_LENGTH, CAR_WIDTH)

        pygame.draw.rect(screen, CAR_COLOR, rect)

    def is_near(self, intersection, threshold=35):
        if self.direction == "N":
            return abs(self.x - intersection.cx) < 10 and 0 < self.front_position() - intersection.cy < threshold
        if self.direction == "S":
            return abs(self.x - intersection.cx) < 10 and 0 < intersection.cy - self.front_position() < threshold
        if self.direction == "E":
            return abs(self.y - intersection.cy) < 10 and 0 < intersection.cx - self.front_position() < threshold
        if self.direction == "W":
            return abs(self.y - intersection.cy) < 10 and 0 < self.front_position() - intersection.cx < threshold
        return False


    def can_go(self, intersection):
        if intersection.phase == "ALL_RED":
            return False
        if self.direction in ("N", "S") and intersection.phase == "NS":
            return True
        if self.direction in ("E", "W") and intersection.phase == "EW":
            return True
        return False

    def car_blocking_ahead(self, cars):
        for other in cars:
            if other is self:
                continue
            if not self.is_in_same_lane(other):
                continue
            edge_gap = self.edge_distance_to(other)
            if self.state == "waiting":
                if edge_gap < CAR_START_GAP:  # distance needed to *start moving*
                    return True
            else:
                if edge_gap < CAR_STOP_GAP:  # distance needed to *stop*
                    return True
        return False

    

    def edge_distance_to(self, other):
        if self.direction == "N":
            return (self.y - CAR_LENGTH / 2) - (other.y + CAR_LENGTH / 2)
        if self.direction == "S":
            return (other.y - CAR_LENGTH / 2) - (self.y + CAR_LENGTH / 2)
        if self.direction == "E":
            return (other.x - CAR_LENGTH / 2) - (self.x + CAR_LENGTH / 2)
        if self.direction == "W":
            return (self.x - CAR_LENGTH / 2) - (other.x + CAR_LENGTH / 2)
        return 9999

    

    def is_in_same_lane(self, other):
        if self.direction == "N" and other.direction == "N":
            return abs(self.x - other.x) < 10 and self.y > other.y
        if self.direction == "S" and other.direction == "S":
            return abs(self.x - other.x) < 10 and self.y < other.y
        if self.direction == "E" and other.direction == "E":
            return abs(self.y - other.y) < 10 and self.x < other.x
        if self.direction == "W" and other.direction == "W":
            return abs(self.y - other.y) < 10 and self.x > other.x
        return False

    def distance_to(self, other):
        if self.direction in ("N", "S"):
            return abs(self.y - other.y)
        else:
            return abs(self.x - other.x)
        
    def front_position(self):
        if self.direction == "N":
            return self.y - self.length / 2
        elif self.direction == "S":
            return self.y + self.length / 2
        elif self.direction == "E":
            return self.x + self.length / 2
        elif self.direction == "W":
            return self.x - self.length / 2
        
    def get_nearest_intersection(self, intersections):
        min_dist = float("inf")
        nearest = None
        for inter in intersections:
            dist = math.hypot(self.x - inter.cx, self.y - inter.cy)
            if dist < min_dist:
                min_dist = dist
                nearest = inter
        return nearest


