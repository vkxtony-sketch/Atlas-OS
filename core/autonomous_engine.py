"""
Atlas OS - Autonomous Engine

This module turns Atlas OS from a request-based system
into a self-running cognitive loop.

It continuously:
- Generates goals (or uses seed goals)
- Executes them via Executive AI
- Evaluates results
- Feeds improvements back into the loop
"""

import time
from typing import List, Dict, Any

from core.executive_ai import ExecutiveAI

class AutonomousEngine:
    def __init__(self, seed_goals: List[str] = None, interval: int = 5):
        self.executive = ExecutiveAI()
        self.seed_goals = seed_goals or [
            "improve system design",
            "optimize agent performance",
            "generate better solutions"
        ]
        self.interval = interval
        self.history: List[Dict[str, Any]] = []
        self.running = False

    def step(self, goal: str) -> Dict[str, Any]:
        result = self.executive.run_goal(goal)
        record = {
            "goal": goal,
            "result": result,
            "timestamp": time.time()
        }
        self.history.append(record)
        return record

    def run_once(self):
        for goal in self.seed_goals:
            self.step(goal)

    def run_forever(self, max_cycles: int = 10):
        self.running = True
        cycle = 0

        while self.running and cycle < max_cycles:
            for goal in self.seed_goals:
                self.step(goal)
                time.sleep(self.interval)
            cycle += 1

        self.running = False

    def stop(self):
        self.running = False

    def get_history(self):
        return self.history
