"""Atlas OS - echo provider (used by tests)."""
from __future__ import annotations

from typing import Any, Dict, Optional

from core.llm_providers.base import Capability, LLMProvider


class EchoProvider(LLMProvider):
    name = "echo"

    def capabilities(self) -> Capability:
        return Capability(streaming=False, tool_use=False, json_mode=False)

    def complete(self, prompt: str, *, system: Optional[str] = None,
                 options: Optional[Dict[str, Any]] = None) -> str:
        return prompt
