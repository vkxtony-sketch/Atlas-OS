"""
Atlas OS - Critic Agent

The Critic Agent is responsible for:
- Evaluating outputs from other agents
- Scoring correctness, clarity, and completeness
- Providing structured feedback for improvement
"""

from typing import Any, Dict
from core.agent import Agent
from core.task import Task


class CriticAgent(Agent):
    def __init__(self):
        super().__init__(name="critic_agent", role="critique")

    def run(self, task: Task) -> Dict[str, Any]:
        goal = task.goal
        payload = task.metadata or {}

        planner_output = payload.get("planner_output")
        coding_output = payload.get("coding_output")
        research_output = payload.get("research_output")

        issues = []
        score = 100

        if not planner_output:
            issues.append("Missing plan from Planner Agent")
            score -= 30

        if not coding_output:
            issues.append("Missing output from Coding Agent")
            score -= 30

        if not research_output:
            issues.append("Missing research context")
            score -= 20

        if planner_output and len(str(planner_output)) < 20:
            issues.append("Planner output too minimal")
            score -= 10

        if coding_output and "error" in str(coding_output).lower():
            issues.append("Coding output contains errors")
            score -= 20

        score = max(score, 0)
        verdict = "pass" if score >= 70 else "fail"

        return {
            "goal": goal,
            "score": score,
            "verdict": verdict,
            "issues": issues,
            "status": "evaluated"
        }
