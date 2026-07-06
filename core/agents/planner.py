"""
Atlas OS - Planner Agent

Breaks high-level goals into executable sub-tasks.
"""

from core.agents.base import BaseAgent


class PlannerAgent(BaseAgent):
    def __init__(self):
        super().__init__("planner")

    def run(self, goal: str):
        prompt = f"""
You are a planning agent.
Break this goal into 3-6 clear steps:
Goal: {goal}
Return as bullet points.
"""
        plan = self.think(prompt)
        return {
            "agent": self.name,
            "goal": goal,
            "plan": plan
        }
