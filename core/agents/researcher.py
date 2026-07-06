"""
Atlas OS - Research Agent

Uses web tool to gather information for tasks.
"""

from core.agents.base import BaseAgent


class ResearchAgent(BaseAgent):
    def __init__(self):
        super().__init__("researcher")

    def run(self, task: str):
        result = self.act(f"search {task}")

        return {
            "agent": self.name,
            "task": task,
            "research": result
        }
