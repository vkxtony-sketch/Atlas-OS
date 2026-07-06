"""
Atlas OS - Coder Agent

Generates and optionally executes Python code via tools.
"""

from core.agents.base import BaseAgent


class CoderAgent(BaseAgent):
    def __init__(self):
        super().__init__("coder")

    def run(self, task: str):
        prompt = f"""
You are a coding agent.
Write Python code for this task:
{task}
Return only code.
"""

        code = self.think(prompt)
        execution = self.act(f"run python {code}")

        return {
            "agent": self.name,
            "task": task,
            "code": code,
            "execution": execution
        }
