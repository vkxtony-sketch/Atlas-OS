"""
Atlas OS - Base Agent

All agents inherit from this class.
Provides:
- LLM access
- Tool access
- Memory access
- Basic execution interface
"""

from core.llm import LLM
from core.tools.router import ToolRouter
from core.memory.store import MemoryStore


class BaseAgent:
    def __init__(self, name: str):
        self.name = name
        self.llm = LLM()
        self.tools = ToolRouter()
        self.memory = MemoryStore()

    def think(self, prompt: str) -> str:
        self.memory.add({
            "agent": self.name,
            "type": "think",
            "prompt": prompt
        })
        return self.llm.complete(prompt)

    def act(self, task: str):
        result = self.tools.route(task)

        self.memory.add({
            "agent": self.name,
            "type": "act",
            "task": task,
            "result": result
        })

        return result

    def remember(self, data: dict):
        self.memory.add({
            "agent": self.name,
            "type": "manual_memory",
            "data": data
        })

    def recall(self, n: int = 5):
        return self.memory.get_recent(n)

    def run(self, input_data: str):
        raise NotImplementedError
