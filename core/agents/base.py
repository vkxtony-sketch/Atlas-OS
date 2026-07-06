"""
Atlas OS - Base Agent

All agents inherit from this class.
Provides:
- LLM access
- Tool access
- Memory access
- Shared swarm memory awareness
- Learning signal adaptation
"""

from core.llm import LLM
from core.tools.router import ToolRouter
from core.memory.store import MemoryStore
from core.memory.shared_store import SharedMemoryStore
from core.swarm.learning import SwarmLearningEngine


class BaseAgent:
    def __init__(self, name: str):
        self.name = name
        self.llm = LLM()
        self.tools = ToolRouter()

        self.memory = MemoryStore()
        self.shared_memory = SharedMemoryStore()
        self.learning = SwarmLearningEngine()

    def _get_context(self) -> str:
        recent_shared = self.shared_memory.get_recent(5)
        learning_signal = self.learning.analyze()

        return f"""
SWARM CONTEXT:
Recent Shared Memory:
{recent_shared}

Learning Signal:
{learning_signal}
"""

    def think(self, prompt: str) -> str:
        adaptive_prompt = f"""
{self._get_context()}

AGENT: {self.name}
TASK:
{prompt}

INSTRUCTIONS:
Use swarm context and learning signals to improve reasoning.
"""

        self.memory.add({"agent": self.name, "type": "think", "prompt": prompt})

        return self.llm.complete(adaptive_prompt)

    def act(self, task: str):
        result = self.tools.route(task)

        self.memory.add({"agent": self.name, "type": "act", "task": task, "result": result})
        self.shared_memory.add({"agent": self.name, "task": task, "result": result})

        return result

    def remember(self, data: dict):
        self.memory.add({"agent": self.name, "type": "manual_memory", "data": data})

    def recall(self, n: int = 5):
        return self.memory.get_recent(n)

    def run(self, input_data: str):
        raise NotImplementedError
