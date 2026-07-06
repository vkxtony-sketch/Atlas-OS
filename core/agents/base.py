"""
Atlas OS - Base Agent

All agents inherit from this class.
Provides:
- LLM access
- Tool access
- Basic execution interface
"""

from core.llm import LLM
from core.tools.router import ToolRouter


class BaseAgent:
    def __init__(self, name: str):
        self.name = name
        self.llm = LLM()
        self.tools = ToolRouter()

    def think(self, prompt: str) -> str:
        return self.llm.complete(prompt)

    def act(self, task: str):
        return self.tools.route(task)

    def run(self, input_data: str):
        raise NotImplementedError
