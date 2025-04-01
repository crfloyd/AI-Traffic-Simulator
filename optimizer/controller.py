import math
import random
import threading
from optimizer.simulator import Simulator

class AnnealingController:
    def __init__(self, run_interval=15, T_start=100, T_min=1, alpha=0.95):
        self.sim = Simulator()
        self.T = T_start
        self.T_min = T_min
        self.alpha = alpha
        self.interval = run_interval
        self.timer = 0.0

        # self.current_config = [
        #     {
        #         "ns_duration": 5, 
        #         "ew_duration": 5,
        #     }
        #     for _ in range(9)
        # ]
        # self.prev_config = [cfg.copy() for cfg in self.current_config]
        self.current_config = [{"ns_duration": 8, "ew_duration": 2} for _ in range(9)]
        self.prev_config = [cfg.copy() for cfg in self.current_config]

        self.current_fitness = None
        self.best_fitness = None
        self.last_throughput = 0.0
        self.fitness_history = []

        self.last_cars_processed = 0
        self.max_cars_processed = 0

        self.pending_result = None
        self.eval_thread = threading.Thread(target=self.evaluate_and_cleanup, args=(self.current_config,))
        
        self.eval_thread.start()

        self.status_message = "Evaluating initial config..."

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
        fitness, throughput, cars_processed = self.sim.run(new_config, duration=25, return_cars=True)
        self.pending_result = (new_config, fitness, throughput, cars_processed)

    def update(self, dt, grid):
        self.timer += dt

        if self.pending_result:
            new_config, new_fitness, new_throughput, cars_processed = self.pending_result
            self.pending_result = None
            
            print("Config being tested:", new_config)
            print("NS durations:", [cfg['ns_duration'] for cfg in new_config])
            print("EW durations:", [cfg['ew_duration'] for cfg in new_config])

            # Reject configurations that cause gridlock
            if cars_processed == 0:
                print("⚠️ Gridlock detected — rejecting mutation")
                self.status_message = "Rejected: gridlock"
                self.timer = 0
                return

            self.status_message = "Applying new config..."

            if self.current_fitness is None:
                self.current_fitness = new_fitness
                self.best_fitness = new_fitness
                self.best_config = new_config
                print("🔰 Initialized current and best fitness")
            else:
                delta = new_fitness - self.current_fitness
                accept_prob = math.exp(-delta / self.T) if delta > 0 else 1.0
                
                print(f"🔍 Δfitness: {delta:.4f}, T: {self.T:.4f}, p: {accept_prob:.4f}")

                if random.random() < accept_prob:
                    self.current_config = new_config
                    self.current_fitness = new_fitness
                    print("✅ Accepted new config")

                    if new_fitness < self.best_fitness:
                        self.best_config = new_config
                        self.best_fitness = new_fitness
                        print("🌟 New best fitness:", self.best_fitness)
                else:
                    print("❌ Rejected new config")
                    
                self.T *= self.alpha

            self.last_throughput = new_throughput
            self.last_cars_processed = cars_processed
            self.max_cars_processed = max(self.max_cars_processed, cars_processed)

            self.fitness_history.append(self.best_fitness)
            if len(self.fitness_history) > 100:
                self.fitness_history.pop(0)

            for inter, cfg, old_cfg in zip(grid.intersections, self.current_config, self.prev_config):
                inter.ns_duration = cfg["ns_duration"]
                inter.ew_duration = cfg["ew_duration"]
                
                inter.elapsed = 0.0

                if (
                    cfg["ns_duration"] != old_cfg["ns_duration"] or
                    cfg["ew_duration"] != old_cfg["ew_duration"]
                ):
                    inter.mark_updated()

            self.prev_config = [cfg.copy() for cfg in self.current_config]
            self.status_message = "Waiting for next mutation..."
            self.timer = 0

        elif self.timer >= self.interval and not self.eval_thread:
            self.status_message = "Evaluating new config..."
            new_config = self.mutate(self.current_config)
            self.eval_thread = threading.Thread(target=self.evaluate_and_cleanup, args=(new_config,))
            print("Testing config:", new_config)
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
        }
