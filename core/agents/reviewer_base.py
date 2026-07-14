"""Atlas OS - reviewer agent base.

Shared scaffolding for reviewer-style agents (code / security / performance).
Each reviewer is a deterministic rule-walker over the artefact plus an LLM
critique that contextualises the verdict.
"""
from __future__ import annotations

from typing import Any, Dict, List

from core.agents.base import BaseAgent


class ReviewerBase(BaseAgent):
    """Subclasses must implement ``_static_findings``."""

    category = "reviewer"

    def __init__(self, name: str) -> None:
        super().__init__(name)

    def run(self, payload: Any) -> Dict[str, Any]:
        findings: List[Dict[str, Any]] = []
        try:
            findings = list(self._static_findings(payload))
        except Exception as exc:  # noqa: BLE001
            findings = [{"severity": "minor", "message": f"static review failed: {exc}"}]

        llm_feedback = self.think(
            f"You are a {self.name} reviewer. Summarise the static findings "
            f"below and propose fixes. Findings: {findings}"
        )

        severity_score = {"critical": 40, "major": 20, "minor": 5, "suggestion": 1}
        penalty = sum(severity_score.get(f.get("severity", "minor"), 5) for f in findings)
        score = max(0, 100 - penalty)
        verdict = "pass" if score >= 70 else "fail"

        return {
            "agent": self.name,
            "category": self.category,
            "score": score,
            "verdict": verdict,
            "findings": findings,
            "llm_summary": llm_feedback,
            "status": "reviewed",
        }

    def _static_findings(self, payload: Any) -> List[Dict[str, Any]]:  # pragma: no cover - abstract
        return []
