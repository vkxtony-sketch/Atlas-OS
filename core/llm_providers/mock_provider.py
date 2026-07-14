"""Atlas OS - mock LLM provider.

Deterministic, offline. Returns a clearly-marked "simulated LLM output"
string so downstream logic can run end-to-end without an LLM.

This is the default provider when nothing else is configured and is
always available (no network, no model files).
"""
from __future__ import annotations

import hashlib
from typing import Any, Dict, Optional

from core.llm_providers.base import Capability, LLMProvider


class MockProvider(LLMProvider):
    name = "mock"

    def capabilities(self) -> Capability:
        return Capability(streaming=False, tool_use=False, json_mode=False)

    def complete(self, prompt: str, *, system: Optional[str] = None,
                 options: Optional[Dict[str, Any]] = None) -> str:
        # Use a stable fingerprint so identical inputs produce identical
        # outputs across processes — important for tests.
        digest = hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:8]
        head = (prompt[:200] + "...") if len(prompt) > 200 else prompt
        head_clean = " ".join(head.split())
        return (
            f"[mock-llm:{digest}] Simulated LLM output for prompt starting with: "
            f"\"{head_clean}\""
        )
