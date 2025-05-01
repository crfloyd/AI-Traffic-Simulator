import pygame
import math

CAR_WIDTH = 12
CAR_LENGTH = 20
CAR_COLOR = (0, 200, 255)
CAR_STOP_GAP = 15
CAR_START_GAP = 35

class Car:
    def __init__(self, x, y, direction, max_speed=100, acceleration=50):
        self.x = x
        self.y = y
        self.direction = direction  # "N", "S", "E", "W"
        self.velocity = 0.0
        self.max_speed = max_speed
        self.acceleration = acceleration
        self.state = "moving"  # or "waiting"
        self.stopped_time = 0.0
        self.length = CAR_LENGTH
        self.width = CAR_WIDTH
        self.spawn_x = x
        self.spawn_y = y
        self.entered_grid = False
        self.age = 0.0


    def update(self, intersections, dt, cars):
        self.age += dt

        # Check if car has moved far enough to start obeying intersections
        if not self.entered_grid:
            dist_from_start = math.hypot(self.x - self.spawn_x, self.y - self.spawn_y)
            if dist_from_start > 100:
                self.entered_grid = True

        near_intersection = (
            self.entered_grid and 
            any(self.is_near(inter) and not self.can_go(inter) for inter in intersections)
        )

        if near_intersection or self.car_blocking_ahead(cars):
            # Stop if there's a red light or car blocking
            self.velocity = 0.0
            self.state = "waiting"
            self.stopped_time += dt
            return
        else:
            # Accelerate
            target_speed = self.max_speed * getattr(self, 'road_speed_factor', 1.0)
            accel_rate = self.acceleration * dt

            # Smooth acceleration using linear interpolation
            if self.velocity < target_speed:
                self.velocity += accel_rate
                self.velocity = min(self.velocity, target_speed)
            elif self.velocity > target_speed:
                self.velocity -= accel_rate  # for future use if speed limits drop
                self.velocity = max(self.velocity, target_speed)


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
        lane_tolerance = 16  

        if self.direction == "N":
            return abs(self.x - intersection.cx) < lane_tolerance and 0 < self.front_position() - intersection.cy < threshold
        if self.direction == "S":
            return abs(self.x - intersection.cx) < lane_tolerance and 0 < intersection.cy - self.front_position() < threshold
        if self.direction == "E":
            return abs(self.y - intersection.cy) < lane_tolerance and 0 < intersection.cx - self.front_position() < threshold
        if self.direction == "W":
            return abs(self.y - intersection.cy) < lane_tolerance and 0 < self.front_position() - intersection.cx < threshold

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
                if edge_gap < CAR_STOP_GAP:
                    return True
            else:
                if edge_gap < CAR_START_GAP:
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
        lane_tolerance = 4  # Must be tighter now that cars are offset

        if self.direction == "N" and other.direction == "N":
            return abs(self.x - other.x) < lane_tolerance and self.y > other.y
        if self.direction == "S" and other.direction == "S":
            return abs(self.x - other.x) < lane_tolerance and self.y < other.y
        if self.direction == "E" and other.direction == "E":
            return abs(self.y - other.y) < lane_tolerance and self.x < other.x
        if self.direction == "W" and other.direction == "W":
            return abs(self.y - other.y) < lane_tolerance and self.x > other.x

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


    def is_actively_waiting(self, intersection):
        return self.state == "waiting" and not self.can_go(intersection) and self.velocity < 0.01
    
    
LANE_OFFSET = 10
def compute_lane_offset(direction, lane_spacing=LANE_OFFSET):
    if direction == 'N':  return (+lane_spacing, 0)   # right side of vertical road
    if direction == 'S':  return (-lane_spacing, 0)   # left side of vertical road
    if direction == 'E':  return (0, +lane_spacing)   # bottom side of horizontal road ✅ flip
    if direction == 'W':  return (0, -lane_spacing)   # top side of horizontal road ✅ flip



