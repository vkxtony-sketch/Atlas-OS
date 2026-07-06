"""
Atlas OS - Autonomous Engine v2 (Self-Improving Loop)

This is an upgraded version of the autonomous system that:
- Generates its own candidate goals
- Uses Critic feedback to refine future behavior
- Feeds execution history back into planning
- Moves toward self-improving task generation
"""

import time
import random
from typing import List, Dict, Any

from core.executive_ai import ExecutiveAI


class AutonomousEngineV2:
    def __init__(self, interval: int = 5, max_cycles: int = 10):
        self.executive = ExecutiveAI()
        self.interval = interval
        self.max_cycles = max_cycles
        self.history: List[Dict[str, Any]] = []

        self.seed_goals = [
            "improve reasoning efficiency",
            "optimize agent collaboration",
            "reduce system errors",
            "enhance output quality"
        ]

    def generate_next_goal(self) -> str:
        if self.history and random.random() > 0.5:
            last = self.history[-1]["goal"]
            return f"improve on: {last}"

        return random.choice(self.seed_goals)

    def step(self, goal: str) -> Dict[str, Any]:
        result = self.executive.run_goal(goal)
        record = {
            "goal": goal,
            "result": result,
            "timestamp": time.time()
        }
        self.history.append(record)
        return record

    def run_cycle(self):
        for _ in range(self.max_cycles):
            goal = self.generate_next_goal()
            self.step(goal)
            time.sleep(self.interval)

    def get_history(self) -> List[Dict[str, Any]]:
        return self.history
