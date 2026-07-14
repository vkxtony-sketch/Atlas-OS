"""Atlas OS - Deployment Agent.

Prepares a *plan* for deploy operations. Real run/deploy happens behind
the permission gate; this agent's role is to synthesise a deploy plan
plus release notes.
"""
from __future__ import annotations

from typing import Any, Dict

from core.agents.base import BaseAgent


class DeploymentAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__("deployment")

    def run(self, payload: Any) -> Dict[str, Any]:
        if isinstance(payload, dict):
            version = str(payload.get("version", "0.1.0"))
            notes = payload.get("notes") or []
        else:
            version = "0.1.0"
            notes = [str(payload)]

        prompt = (
            "Produce release notes (Markdown) for the following version. "
            f"Version: {version}\nNotes: {notes}"
        )
        text = self.think(prompt)

        return {
            "agent": self.name,
            "version": version,
            "plan": self._plan(),
            "release_notes": text,
            "status": "planned",
        }

    @staticmethod
    def _plan() -> Dict[str, str]:
        return {
            "build": "python -m build",
            "test": "pytest -q",
            "package": "docker build -t atlas-os:dev .",
            "deploy": "ATLAS_ALLOW_DEPLOY=true (NOT enabled by default) "
                      "→ external pipeline.",
        }
