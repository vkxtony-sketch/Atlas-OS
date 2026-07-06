"""
Atlas OS - Base Agent System

All agents in Atlas OS inherit from this base class.
Agents consume Tasks and produce results.
"""

from typing import Any, Dict
from core.task import Task


class Agent:
    """Base class for all Atlas OS agents."""

    def __init__(self, name: str, role: str = "general"):
        self.name = name
        self.role = role
        self.state: Dict[str, Any] = {}

    def can_handle(self, task: Task) -> bool:
        return task.task_type in ["general", self.role]

    def run(self, task: Task) -> Any:
        raise NotImplementedError("Agent must implement run()")

    def update_state(self, key: str, value: Any):
        self.state[key] = value

    def get_state(self, key: str, default: Any = None) -> Any:
        return self.state.get(key, default)
