"""Atlas OS - Performance Reviewer Agent."""
from __future__ import annotations

import re
from typing import Any, Dict, List

from core.agents.reviewer_base import ReviewerBase


class PerformanceReviewerAgent(ReviewerBase):
    category = "performance_review"

    def __init__(self) -> None:
        super().__init__("performance_reviewer")

    _NESTED_LOOP = re.compile(r"for .+ in .+:\s*\n(?:\s+for .+ in .+:\s*\n)", re.M)
    _SLEEP = re.compile(r"\btime\.sleep\s*\(\s*(\d+(?:\.\d+)?)\s*\)")
    _READ_ALL = re.compile(r"\b(?:read|readlines|load)\(\s*\)")

    def _static_findings(self, payload: Any) -> List[Dict[str, Any]]:
        from core.agents.code_reviewer import CodeReviewerAgent  # local helper
        text = CodeReviewerAgent._extract_text(payload)
        findings: List[Dict[str, Any]] = []
        if not text:
            return findings

        if self._NESTED_LOOP.search(text):
            findings.append(
                {"severity": "major", "rule": "nested-loop",
                 "message": "Nested for-loop detected; consider O(n) alternatives "
                             "(hash maps, sort+two-pointer, numpy)."}
            )
        for m in self._SLEEP.finditer(text):
            try:
                secs = float(m.group(1))
            except Exception:
                continue
            if secs >= 1.0:
                findings.append(
                    {"severity": "minor", "rule": "long-sleep",
                     "message": f"time.sleep({secs}) is >= 1s; prefer event-driven waits."}
                )
        if self._READ_ALL.search(text):
            findings.append(
                {"severity": "suggestion", "rule": "unbounded-read",
                 "message": "Unbounded read() — stream large files instead."}
            )
        return findings
