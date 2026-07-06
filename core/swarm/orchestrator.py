"""
Atlas OS - Final Swarm Orchestrator

This is the top-level autonomous system controller.
It wires together ALL agents into a continuous loop:

Planner -> Researcher -> Coder -> Critic -> Feedback

This is the final "swarm intelligence runtime" layer.
"""

import time
from typing import Dict, Any

from core.agents.planner import PlannerAgent
from core.agents.researcher import ResearchAgent
from core.agents.coder import CoderAgent
from core.agents.critic import CriticAgent


class SwarmOrchestrator:
    def __init__(self, interval: int = 5, max_cycles: int = 5):
        self.planner = PlannerAgent()
        self.researcher = ResearchAgent()
        self.coder = CoderAgent()
        self.critic = CriticAgent()

        self.interval = interval
        self.max_cycles = max_cycles
        self.history = []

    def run_cycle(self, goal: str) -> Dict[str, Any]:
        plan = self.planner.run(goal)
        research = self.researcher.run(goal)
        code = self.coder.run(goal)
        evaluation = self.critic.run({
            "goal": goal,
            "plan": plan,
            "research": research,
            "code": code
        })

        result = {
            "goal": goal,
            "plan": plan,
            "research": research,
            "code": code,
            "evaluation": evaluation
        }

        self.history.append(result)
        return result

    def run(self, seed_goal: str):
        current_goal = seed_goal

        for i in range(self.max_cycles):
            print(f"[SWARM] Cycle {i+1}/{self.max_cycles}: {current_goal}")

            result = self.run_cycle(current_goal)

            try:
                eval_text = str(result["evaluation"])
                if "low" in eval_text.lower() or "bad" in eval_text.lower():
                    current_goal = f"improve: {current_goal}"
                else:
                    current_goal = f"enhance: {current_goal}"
            except Exception:
                current_goal = f"refine: {current_goal}"

            time.sleep(self.interval)

        return self.history
