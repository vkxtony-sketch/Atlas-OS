"""Atlas OS - QA Engineer Agent."""
from __future__ import annotations

from typing import Any, Dict, List

from core.agents.base import BaseAgent


class QAEngineerAgent(BaseAgent):
    """Generates a test plan + edge cases from the goal/plan."""

    def __init__(self) -> None:
        super().__init__("qa_engineer")

    def run(self, payload: Any) -> Dict[str, Any]:
        if isinstance(payload, dict):
            goal = str(payload.get("goal", ""))
            plan = payload.get("plan") or {}
            risks = payload.get("risks") or []
        else:
            goal = str(payload)
            plan = {}
            risks = []

        prompt = (
            "Produce a pytest-style test outline AND a list of edge cases.\n"
            f"Goal: {goal}\nPlan: {plan}\nKnown risks: {risks}\n"
        )
        text = self.think(prompt)

        cases: List[str] = []
        for line in text.splitlines():
            line = line.strip()
            if line.startswith(("-", "*", "1.", "2.", "3.", "4.", "5.")):
                cases.append(line.lstrip("-*0123456789. ").strip())

        return {
            "agent": self.name,
            "test_outline": text,
            "edge_cases": cases[:10],
            "status": "planned" if text else "empty",
        }
