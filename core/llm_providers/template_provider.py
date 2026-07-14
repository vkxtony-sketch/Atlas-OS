"""Atlas OS - template provider.

A deterministic, offline "LLM" that produces *structured* responses by
recognising a few prompt keywords and choosing canned templates. Useful
for environments where network access is impossible but you still want
behaviour that isn't completely vacuous.
"""
from __future__ import annotations

import re
from typing import Any, Dict, Optional

from core.llm_providers.base import Capability, LLMProvider


_STEP_HEAD = re.compile(r"\b(?:step|how|plan|design|architect)\b", re.I)
_QUESTION_HEAD = re.compile(r"\b(?:what|why|how|explain|describe)\b", re.I)
_CODE_HINT = re.compile(r"\b(?:code|function|class|implement|generate)\b", re.I)
_RESEARCH_HINT = re.compile(r"\b(?:research|search|find|compare|investigate)\b", re.I)


class TemplateProvider(LLMProvider):
    name = "template"

    def capabilities(self) -> Capability:
        return Capability(streaming=False, tool_use=False, json_mode=False)

    def complete(self, prompt: str, *, system: Optional[str] = None,
                 options: Optional[Dict[str, Any]] = None) -> str:
        body = prompt.strip()
        if not body:
            return "[template-llm] (empty prompt)"

        if _STEP_HEAD.search(body) or _CODE_HINT.search(body):
            return self._step_template(body)
        if _RESEARCH_HINT.search(body):
            return self._research_template(body)
        if _QUESTION_HEAD.search(body):
            return self._qa_template(body)
        return self._summary_template(body)

    def _step_template(self, prompt: str) -> str:
        topic = prompt.split("\n", 1)[0][:120].strip()
        return (
            "[template-llm:steps]\n"
            f"Topic: {topic}\n"
            "1. Restate the goal succinctly.\n"
            "2. Identify the smallest concrete deliverable.\n"
            "3. List 3-6 ordered steps to reach it.\n"
            "4. Note the risks and unknowns.\n"
            "5. Define acceptance criteria.\n"
        )

    def _research_template(self, prompt: str) -> str:
        topic = prompt.split("\n", 1)[0][:120].strip()
        return (
            "[template-llm:research]\n"
            f"Query: {topic}\n"
            "- Trust official documentation first.\n"
            "- Cross-check against recent GitHub projects.\n"
            "- Note disagreements rather than hiding them.\n"
            "- Cite the source URL next to each claim.\n"
        )

    def _qa_template(self, prompt: str) -> str:
        return (
            "[template-llm:qa]\n"
            f"Question: {prompt[:160]}\n"
            "Best-effort offline answer: see Atlas OS knowledge index "
            "(`atlas_knowledge/`) for any indexed documents.\n"
        )

    def _summary_template(self, prompt: str) -> str:
        head = " ".join(prompt.split())[:200]
        return f"[template-llm:summary] {head}"
