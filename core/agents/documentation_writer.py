"""Atlas OS - Documentation Writer Agent."""
from __future__ import annotations

from typing import Any, Dict

from core.agents.base import BaseAgent


class DocumentationWriterAgent(BaseAgent):
    """Synthesises documentation from a goal + plan + code snippet."""

    def __init__(self) -> None:
        super().__init__("documentation_writer")

    def run(self, payload: Any) -> Dict[str, Any]:
        if isinstance(payload, dict):
            goal = str(payload.get("goal", ""))
            plan = payload.get("plan") or {}
            code = payload.get("code") or ""
        else:
            goal = str(payload)
            plan = {}
            code = ""

        prompt = (
            "Generate a README outline AND an API doc stub for the following.\n"
            f"Goal: {goal}\n"
            f"Plan: {plan}\n"
            f"Code (truncated): {str(code)[:1200]}\n"
        )
        text = self.think(prompt)

        return {
            "agent": self.name,
            "readme_outline": self._outline(text, kind="readme"),
            "api_stub": self._outline(text, kind="api"),
            "raw": text,
            "status": "documented" if text else "empty",
        }

    @staticmethod
    def _outline(text: str, kind: str) -> str:
        head = text.strip().splitlines()[:6]
        bullets = [f"- {line.strip('- ').strip()}" for line in head if line.strip()]
        if kind == "readme":
            section = "README"
        else:
            section = "API"
        out = [f"## {section}", ""] + (bullets or ["- (no content)"])
        return "\n".join(out)
