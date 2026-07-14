"""Atlas OS - Planner Agent.

The Planner MUST produce a structured, list-shaped plan (not a single
string) so downstream agents can read individual steps. The LLM is asked
for a brief rationale; the plan-shape itself is generated deterministically
with a sensible 4-step default that the LLM rationale can annotate.
"""
from __future__ import annotations

from typing import Any, Dict, List

from core.agents.base import BaseAgent


class PlannerAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__("planner")

    def run(self, goal: Any) -> Dict[str, Any]:
        goal_text = str(goal) if not isinstance(goal, str) else goal

        structured: List[Dict[str, str]] = [
            {
                "step": "1",
                "title": "Understand goal",
                "description": f"Analyze requirements for: {goal_text}",
            },
            {
                "step": "2",
                "title": "Decompose problem",
                "description": f"Break {goal_text} into subcomponents",
            },
            {
                "step": "3",
                "title": "Define execution strategy",
                "description": f"Determine approach to solve {goal_text}",
            },
            {
                "step": "4",
                "title": "Validate plan",
                "description": f"Check completeness and risks for {goal_text}",
            },
        ]

        # Let the LLM contribute an annotated rationale (string) alongside
        # the structured plan. Don't let it replace the plan shape.
        rationale = self.think(
            "Provide a brief rationale (no more than 4 sentences) for this "
            f"plan: {structured}"
        )

        return {
            "agent": self.name,
            "goal": goal_text,
            "plan": structured,        # list of step dicts (the contract)
            "rationale": rationale,   # free-form LLM commentary
            "dependencies": [],
            "status": "planned",
        }
