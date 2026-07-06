"""
Atlas OS - Task Model

A Task is the fundamental unit of work in Atlas OS.
Every agent, executive decision, and consensus step operates on Tasks.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import time

@dataclass
class Task:
    id: str
    goal: str
    task_type: str = "general"
    status: str = "pending"
    priority: int = 1

    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    metadata: Dict[str, Any] = field(default_factory=dict)
    result: Optional[Any] = None
    error: Optional[str] = None

    dependencies: List[str] = field(default_factory=list)
    assigned_agent: Optional[str] = None

    def mark_running(self):
        self.status = "running"
        self.updated_at = time.time()

    def mark_complete(self, result: Any):
        self.status = "complete"
        self.result = result
        self.updated_at = time.time()

    def mark_failed(self, error: str):
        self.status = "failed"
        self.error = error
        self.updated_at = time.time()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "goal": self.goal,
            "task_type": self.task_type,
            "status": self.status,
            "priority": self.priority,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": self.metadata,
            "result": self.result,
            "error": self.error,
            "dependencies": self.dependencies,
            "assigned_agent": self.assigned_agent,
        }