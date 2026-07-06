"""
Atlas OS - Autonomous Engine v3 (Critic-Driven Evolution Loop)

This is the final evolution layer of Atlas OS autonomous behavior.

Upgrades over v2:
- Uses execution history + critic scores to guide goal generation
- Prioritizes improving low-performing tasks
- Introduces weighted memory-based goal selection
- Moves closer to self-optimizing behavior loop
"""

import time
import random
from typing import List, Dict, Any

from core.executive_ai import ExecutiveAI


class AutonomousEngineV3:
    def __init__(self, interval: int = 5, max_cycles: int = 10):
        self.executive = ExecutiveAI()
        self.interval = interval
        self.max_cycles = max_cycles

        self.history: List[Dict[str, Any]] = []

        self.seed_goals = [
            "improve reasoning efficiency",
            "optimize agent collaboration",
            "reduce system errors",
            "enhance output quality",
            "increase consensus accuracy"
        ]

    def _get_last_score(self, result: Dict[str, Any]) -> float:
        try:
            return result.get("critic", {}).get("score", 50)
        except Exception:
            return 50

    def generate_next_goal(self) -> str:
        if not self.history:
            return random.choice(self.seed_goals)

        last_record = self.history[-1]
        last_goal = last_record["goal"]
        last_score = self._get_last_score(last_record["result"])

        if last_score < 70:
            return f"fix weaknesses in: {last_goal}"

        if random.random() > 0.5:
            return f"enhance further: {last_goal}"

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
