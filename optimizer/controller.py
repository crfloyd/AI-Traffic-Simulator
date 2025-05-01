import math
import random
import threading
import pygame
from optimizer.simulator import Simulator
from simulation.grid import GRID_ROWS, GRID_COLS, Grid

class AnnealingController:
    STATUS_INIT = "Evaluating initial config..."
    STATUS_OPTIMIZATION_DONE = "Optimization complete"
    STATUS_REJECTED = "Rejected: gridlock"
    STATUS_APPLYING = "Applying new config..."
    STATUS_BEST_INITIALIZED = "Config initialized"
    STATUS_BEST_APPLIED = "Better config found!"
    STATUS_WAITING = "Waiting for next sim"
    STATUS_EVALUATING = "Evaluating new config..."

    def __init__(self, grid, run_interval=10, T_start=150, T_min=1, alpha=0.95):
        self.grid = grid
        self.eval_thread = None
        self.pending_first_eval = True
        self.sim = Simulator()
        self.T = T_start
        self.T_min = T_min
        self.alpha = alpha
        self.interval = run_interval
        self.timer = 0.0
        self.optimization_locked = False
        self.show_heatmap = True


        num_intersections = GRID_ROWS * GRID_COLS
        self.current_config = [
            {"ns_duration": 10, "ew_duration": 3} if i % 2 == 0 else {"ns_duration": 3, "ew_duration": 10}
            for i in range(num_intersections)
        ]


        self.prev_config = [cfg.copy() for cfg in self.current_config]
        self.best_config = self.current_config.copy()

        self.current_fitness = None
        self.best_fitness = None
        self.last_throughput = 0.0
        self.fitness_history = []

        self.last_cars_processed = 0
        self.max_cars_processed = 0

        self.pending_result = None
        self.eval_thread = threading.Thread(target=self.evaluate_and_cleanup, args=(self.current_config,))
        self.eval_thread.start()

        self.status_message = self.STATUS_INIT

    def mutate(self, config_list):
        def clamp(value, min_val, max_val):
            return max(min_val, min(value, max_val))

        new_config = [cfg.copy() for cfg in config_list]

        num_to_mutate = random.randint(1, 2)
        for _ in range(num_to_mutate):
            i = random.randint(0, len(new_config) - 1)
            new_config[i]["ns_duration"] += random.choice([-1, 1])
            new_config[i]["ew_duration"] += random.choice([-1, 1])
            new_config[i]["ns_duration"] = clamp(new_config[i]["ns_duration"], 3, 10)
            new_config[i]["ew_duration"] = clamp(new_config[i]["ew_duration"], 3, 10)

        return new_config

    def evaluate_in_background(self, new_config):
        duration = self.get_dynamic_duration()
        print(f"⏱ Sim duration: {duration}s at T={self.T:.2f}")
        import time
        start = time.time()
        fitness, throughput, cars_processed = self.sim.run(new_config, duration=duration, return_cars=True)
        print(f"[Eval Done] Real time: {time.time() - start:.3f}s")
        self.pending_result = (new_config, fitness, throughput, cars_processed)

    def get_dynamic_duration(self):
        temp = max(self.T_min, min(self.T, 100))
        return int(20 + (90 - 20) * (1 - (temp - self.T_min) / (100 - self.T_min)))

    def update(self, dt):
        if getattr(self, "pending_first_eval", False):
            self.status_message = self.STATUS_EVALUATING
            self.eval_thread = threading.Thread(target=self.evaluate_and_cleanup, args=(self.current_config,))
            self.eval_thread.start()
            self.pending_first_eval = False
            
        if self.status_message == self.STATUS_OPTIMIZATION_DONE:
            return

        self.timer += dt

        if self.T <= self.T_min and not self.eval_thread and not self.optimization_locked:
            print("🌡️ Optimization complete — locking best config")
            self.current_config = self.best_config
            self.status_message = self.STATUS_OPTIMIZATION_DONE
            self.optimization_locked = True 

            for inter, cfg in zip(self.grid.intersections, self.best_config):
                inter.ns_duration = cfg["ns_duration"]
                inter.ew_duration = cfg["ew_duration"]
                inter.elapsed = 0.0
                inter.mark_updated()

            self.grid.cars.clear()
            self.grid.total_wait_time = 0.0
            self.grid.cars_processed = 0
            self.grid.avg_wait_time = 0.0

            self.prev_config = [cfg.copy() for cfg in self.current_config]
            return

        if self.pending_result:
            new_config, new_fitness, new_throughput, cars_processed = self.pending_result
            self.pending_result = None

            if cars_processed == 0:
                print("⚠️ Grid gridlock detected — rejecting mutation")
                self.status_message = self.STATUS_REJECTED
                self.timer = 0
                return

            self.status_message = self.STATUS_APPLYING

            if self.current_fitness is None:
                self.current_fitness = new_fitness
                self.best_fitness = new_fitness
                self.best_config = new_config
                
                # Apply best config visually
                for inter, cfg in zip(self.grid.intersections, new_config):
                    inter.ns_duration = cfg["ns_duration"]
                    inter.ew_duration = cfg["ew_duration"]
                    inter.elapsed = 0.0
                    inter.mark_updated()

                self.grid.cars.clear()
                self.grid.total_wait_time = 0.0
                self.grid.cars_processed = 0
                self.grid.avg_wait_time = 0.0

                self.status_message = self.STATUS_BEST_INITIALIZED

            else:
                delta = new_fitness - self.current_fitness
                accept_prob = math.exp(-delta / self.T) if delta > 0 else 1.0

                if random.random() < accept_prob:
                    self.current_config = new_config
                    self.current_fitness = new_fitness

                    if new_fitness < self.best_fitness:
                        self.best_config = new_config
                        self.best_fitness = new_fitness
                        print("🌟 New best fitness:", self.best_fitness)

                        self.grid.cars.clear()
                        self.grid.total_wait_time = 0.0
                        self.grid.cars_processed = 0
                        self.grid.avg_wait_time = 0.0
                        self.status_message = self.STATUS_BEST_APPLIED

                else:
                    print("❌ Rejected new config")

                if self.status_message != self.STATUS_OPTIMIZATION_DONE:
                    self.T *= self.alpha


            self.last_throughput = new_throughput
            self.last_cars_processed = cars_processed
            self.max_cars_processed = max(self.max_cars_processed, cars_processed)

            self.fitness_history.append(self.best_fitness)
            if len(self.fitness_history) > 100:
                self.fitness_history.pop(0)

            for inter, cfg, old_cfg in zip(self.grid.intersections, self.current_config, self.prev_config):
                inter.ns_duration = cfg["ns_duration"]
                inter.ew_duration = cfg["ew_duration"]
                inter.elapsed = 0.0

                if self.T > self.T_min:
                    if (
                        cfg["ns_duration"] != old_cfg["ns_duration"] or
                        cfg["ew_duration"] != old_cfg["ew_duration"]
                    ):
                        inter.mark_updated()

            self.prev_config = [cfg.copy() for cfg in self.current_config]
            if self.status_message not in (self.STATUS_BEST_INITIALIZED, self.STATUS_BEST_APPLIED):
                self.status_message = self.STATUS_WAITING
            self.timer = 0

        elif self.timer >= self.interval and not self.eval_thread:
            self.status_message = self.STATUS_EVALUATING
            new_config = self.mutate(self.current_config)
            self.eval_thread = threading.Thread(target=self.evaluate_and_cleanup, args=(new_config,))
            self.eval_thread.start()

    def evaluate_and_cleanup(self, new_config):
        self.evaluate_in_background(new_config)
        self.eval_thread = None

    def get_debug_info(self):
        return {
            "best_fitness": self.best_fitness if self.best_fitness is not None else 0.0,
            "current_fitness": self.current_fitness if self.current_fitness is not None else 0.0,
            "temperature": self.T,
            "current_config": self.current_config,
            "countdown": max(0.0, self.interval - self.timer),
            "fitness_history": self.fitness_history,
            "status": self.status_message,
            "throughput": self.last_throughput,
            "cars_processed": self.last_cars_processed,
            "max_cars": self.max_cars_processed,
            "cars_in_grid": len(self.grid.cars),
            "avg_stopped_time": sum(c.stopped_time for c in self.grid.cars) / len(self.grid.cars) if self.grid.cars else 0.0,

        }
