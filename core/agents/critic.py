"""
Atlas OS - Critic Agent

Evaluates outputs and assigns a quality score.
"""

from core.agents.base import BaseAgent


class CriticAgent(BaseAgent):
    def __init__(self):
        super().__init__("critic")

    def run(self, data: dict):
        prompt = f"""
You are a critic agent.
Evaluate this output:
{data}

Return:
- score (0-100)
- brief explanation
"""

        evaluation = self.think(prompt)

        return {
            "agent": self.name,
            "evaluation": evaluation
        }
