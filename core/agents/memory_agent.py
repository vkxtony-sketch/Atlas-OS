"""Atlas OS - Memory Agent.

Thin facade that reads from the project's ``MemoryStore`` and writes
back structured entries. Real long-term tiers would split short-term
context-window storage from durable persistent storage; this build uses
one JSON-backed ``MemoryStore`` per project.
"""
from __future__ import annotations

from typing import Any, Dict

from core.agents.base import BaseAgent
from core.memory.store import MemoryStore
from core.config import get_settings


class MemoryAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__("memory")
        self._store = MemoryStore(path=get_settings().memory_path)

    def run(self, payload: Any) -> Dict[str, Any]:
        if not isinstance(payload, dict):
            payload = {"kind": "concept", "data": str(payload)}

        kind = str(payload.get("kind", "concept"))
        data = payload.get("data")
        if kind == "recall":
            try:
                n = int(payload.get("n", 5))
            except Exception:
                n = 5
            data = self._store.get_recent(n)
        else:
            self._store.add({"kind": kind, "data": data, "agent": self.name})

        return {
            "agent": self.name,
            "kind": kind,
            "data": data,
            "status": "served" if data is not None else "empty",
        }
