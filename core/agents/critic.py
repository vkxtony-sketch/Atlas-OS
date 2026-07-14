"""Atlas OS - Critic Agent.

The Critic MUST return a contract dict with at least:
  ``agent``, ``score`` (int 0..100), ``verdict`` ("pass"|"fail"),
  ``issues`` (list[str]), ``feedback`` (str from LLM), ``status``.
"""
from __future__ import annotations

from typing import Any, Dict, List

from core.agents.base import BaseAgent


class CriticAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__("critic")

    def run(self, payload: Any) -> Dict[str, Any]:
        if isinstance(payload, dict):
            planner = payload.get("planner")
            research = payload.get("research")
            coding = payload.get("coding")
            pass_idx = int(payload.get("pass", 0) or 0)
            goal = str(payload.get("goal", ""))
            critic_issues = payload.get("critic_issues", []) or []
        else:
            planner = research = coding = None
            pass_idx = 0
            goal = str(payload)
            critic_issues = []

        # Deterministic base score, then nudge based on completeness.
        score = 100
        issues: List[str] = list(critic_issues)

        if not planner or planner in ("", {}, []):
            issues.append("Planner output missing or empty.")
            score -= 30
        if not coding or coding in ("", {}, []):
            issues.append("Coder output missing or empty.")
            score -= 30

        # If this is a revision pass, give a small boost so convergence
        # can happen even with imperfect outputs.
        if pass_idx > 0 and score >= 60:
            score = min(100, score + 5)

        score = max(0, min(100, int(score)))
        verdict = "pass" if score >= 70 else "fail"

        feedback = self.think(
            "Provide a brief critique. Use one or two sentences.\n"
            f"Goal: {goal}\n"
            f"Issues: {issues}\n"
            f"Pass: {pass_idx}\n"
        )

        return {
            "agent": self.name,
            "goal": goal,
            "score": score,
            "verdict": verdict,
            "issues": issues,
            "feedback": feedback,
            "status": "evaluated",
        }
