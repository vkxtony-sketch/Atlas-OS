"""
Atlas OS - Shared Memory Store (Swarm Memory)

This extends MemoryStore into a global shared memory layer
so all agents can read/write from a single collective memory.

Enables:
- cross-agent learning
- shared experience buffer
- swarm-level adaptation
"""

import json
import os
from typing import Any, Dict, List


class SharedMemoryStore:
    _instance = None

    def __new__(cls, path: str = "atlas_shared_memory.json"):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.path = path
            cls._instance.data = cls._instance._load()
        return cls._instance

    def _load(self) -> Dict[str, Any]:
        if not os.path.exists(self.path):
            return {"shared_history": []}

        try:
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"shared_history": []}

    def save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)

    def add(self, entry: Dict[str, Any]):
        self.data.setdefault("shared_history", []).append(entry)
        self.save()

    def get_recent(self, n: int = 10) -> List[Dict[str, Any]]:
        return self.data.get("shared_history", [])[-n:]

    def get_all(self) -> List[Dict[str, Any]]:
        return self.data.get("shared_history", [])

    def clear(self):
        self.data = {"shared_history": []}
        self.save()
