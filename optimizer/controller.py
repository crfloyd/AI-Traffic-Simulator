import math
import random
from optimizer.simulator import Simulator

class AnnealingController:
    def __init__(self, run_interval=15, T_start=100, T_min=1, alpha=0.95):
        self.sim = Simulator()
        self.T = T_start
        self.T_min = T_min
        self.alpha = alpha
        self.interval = run_interval
        self.timer = 0.0

        self.current_config = self.current_config = [
            {"ns_duration": 5, "ew_duration": 5, "all_red_duration": 2}
            for _ in range(9) 
        ]

        self.current_fitness = self.sim.run(self.current_config, duration=5)

        self.best_config = self.current_config
        self.best_fitness = self.current_fitness

    def mutate(self, config_list):
        new_config = []
        for cfg in config_list:
            new_cfg = {
                "ns_duration": max(2, cfg["ns_duration"] + random.choice([-1, 0, 1])),
                "ew_duration": max(2, cfg["ew_duration"] + random.choice([-1, 0, 1])),
                "all_red_duration": min(2.0, max(1.0, cfg["all_red_duration"] + random.choice([-0.5, 0, 0.5]))),
            }
            new_config.append(new_cfg)
        return new_config


    def update(self, dt, grid):
        self.timer += dt

        if self.T < self.T_min:
            return  # Done

        if self.timer >= self.interval:
            self.timer = 0
            new_config = self.mutate(self.current_config)
            new_fitness = self.sim.run(new_config, duration=5)

            delta = new_fitness - self.current_fitness
            accept_prob = math.exp(-delta / self.T) if delta > 0 else 1.0

            if random.random() < accept_prob:
                self.current_config = new_config
                self.current_fitness = new_fitness

                if new_fitness < self.best_fitness:
                    self.best_config = new_config
                    self.best_fitness = new_fitness

            self.T *= self.alpha

            print(f"Annealing step | T={self.T:.2f} | Current={self.current_fitness:.2f} | Best={self.best_fitness:.2f}")

            # per-intersection configs
            for inter, cfg in zip(grid.intersections, self.current_config):
                inter.ns_duration = cfg["ns_duration"]
                inter.ew_duration = cfg["ew_duration"]
                inter.all_red_duration = cfg["all_red_duration"]
                
    def get_debug_info(self):
        return {
            "best_fitness": self.best_fitness,
            "temperature": self.T,
            "current_config": self.current_config,
            "countdown": max(0.0, self.interval - self.timer),
        }



