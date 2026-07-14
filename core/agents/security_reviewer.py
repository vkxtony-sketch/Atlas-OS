"""Atlas OS - Security Reviewer Agent."""
from __future__ import annotations

import re
from typing import Any, Dict, List

from core.agents.reviewer_base import ReviewerBase


def _extract_text(payload: Any) -> str:
    if isinstance(payload, str):
        return payload
    if isinstance(payload, dict):
        return "\n".join(str(v) for v in payload.values())
    return str(payload)


class SecurityReviewerAgent(ReviewerBase):
    """Detects likely secrets + dangerous call patterns.

    This is a real best-effort pattern-matcher, not a guarantee.
    """

    def __init__(self) -> None:
        super().__init__("security_reviewer")

    category = "security_review"

    _SECRET = re.compile(
        r"(?i)\b(?:api[_-]?key|secret|token|password)\b\s*[:=]\s*[\"']?[A-Za-z0-9_\-]{12,}"
    )
    _EXEC = re.compile(r"\bexec\s*\(")
    _EVAL = re.compile(r"\beval\s*\(")
    _SHELL = re.compile(r"\bsubprocess\.[A-Za-z_]+\(.*shell\s*=\s*True", re.S)
    _PICKLE = re.compile(r"\bpickle\.loads?\(")

    def _static_findings(self, payload: Any) -> List[Dict[str, Any]]:
        text = _extract_text(payload)
        findings: List[Dict[str, Any]] = []
        if not text:
            return findings

        if self._SECRET.search(text):
            findings.append(
                {"severity": "critical", "rule": "possible-secret",
                 "message": "Inline credential pattern detected; use a secrets manager."}
            )
        if self._EXEC.search(text):
            findings.append(
                {"severity": "critical", "rule": "exec-usage",
                 "message": "Use of exec() — code-execution risk; secure-sandbox only."}
            )
        if self._EVAL.search(text):
            findings.append(
                {"severity": "critical", "rule": "eval-usage",
                 "message": "Use of eval() — code-execution risk."}
            )
        if self._SHELL.search(text):
            findings.append(
                {"severity": "major", "rule": "shell-true",
                 "message": "subprocess call with shell=True; risk of shell injection."}
            )
        if self._PICKLE.search(text):
            findings.append(
                {"severity": "major", "rule": "pickle-load",
                 "message": "Pickle deserialisation can execute arbitrary code."}
            )
        return findings
