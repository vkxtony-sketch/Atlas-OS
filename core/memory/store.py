"""
Atlas OS - Memory Store

Simple persistent memory system for agents.
Stores:
- task history
- agent outputs
- evaluation results

Backed by a JSON file on disk.
"""

import json
import os
from typing import Any, Dict, List


class MemoryStore:
    def __init__(self, path: str = "atlas_memory.json"):
        self.path = path
        self.data = self._load()

    def _load(self) -> Dict[str, Any]:
        if not os.path.exists(self.path):
            return {"history": []}

        try:
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"history": []}

    def save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)

    def add(self, entry: Dict[str, Any]):
        self.data.setdefault("history", []).append(entry)
        self.save()

    def get_recent(self, n: int = 5) -> List[Dict[str, Any]]:
        return self.data.get("history", [])[-n:]

    def clear(self):
        self.data = {"history": []}
        self.save()
