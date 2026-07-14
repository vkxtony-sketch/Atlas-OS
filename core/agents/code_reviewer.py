"""Atlas OS - Code Reviewer Agent."""
from __future__ import annotations

import re
from typing import Any, Dict, List

from core.agents.reviewer_base import ReviewerBase


class CodeReviewerAgent(ReviewerBase):
    """Lightweight static review: stub for broken patterns. The spec
    lists dead-code / style enforcement here; we provide a deterministic
    regex walker that flags obvious smells without an AST."""

    category = "code_review"

    def __init__(self) -> None:
        super().__init__("code_reviewer")

    _DEAD_TODO = re.compile(r"\bTODO\b|\bFIXME\b|\bXXX\b")
    _LONG_LINE = re.compile(r".{200,}")
    _DEEP_NEST = re.compile(r"(?:\n[ \t]+){6,}\S")

    def _static_findings(self, payload: Any) -> List[Dict[str, Any]]:
        findings: List[Dict[str, Any]] = []

        text = self._extract_text(payload)
        if not text:
            return findings

        if self._DEAD_TODO.search(text):
            findings.append(
                {"severity": "minor", "rule": "todo-left-in-code",
                 "message": "Unresolved TODO/FIXME/XXX marker detected."}
            )

        for i, line in enumerate(text.splitlines(), 1):
            if self._LONG_LINE.match(line):
                findings.append(
                    {"severity": "suggestion", "rule": "line-too-long",
                     "line": i, "message": "Line exceeds 200 chars; consider wrapping."}
                )

        if self._DEEP_NEST.search(text):
            findings.append(
                {"severity": "major", "rule": "deeply-nested",
                 "message": "Indentation depth >5 levels; extract a helper."}
            )

        return findings

    @staticmethod
    def _extract_text(payload: Any) -> str:
        if isinstance(payload, str):
            return payload
        if isinstance(payload, dict):
            chunks: List[str] = []
            for v in payload.values():
                chunks.append(str(v))
            return "\n".join(chunks)
        return str(payload)
