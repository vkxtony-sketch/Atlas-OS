"""Atlas OS - LLM provider protocol."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class Capability:
    """What a provider can / can't do."""

    streaming: bool = False
    tool_use: bool = False
    json_mode: bool = False
    max_context_chars: int = 8000


class LLMProvider:
    """Abstract interface implemented by every provider driver."""

    name = "abstract"

    def capabilities(self) -> Capability:
        return Capability()

    def complete(self, prompt: str, *, system: Optional[str] = None,
                 options: Optional[Dict[str, Any]] = None) -> str:
        raise NotImplementedError

    # Some agents want a single chat-style invocation (system + user).
    def chat(self, messages: List[Dict[str, str]],
             *, options: Optional[Dict[str, Any]] = None) -> str:
        # Default implementation flattens chat messages into a single prompt.
        parts: List[str] = []
        for m in messages:
            role = m.get("role", "user")
            content = m.get("content", "")
            parts.append(f"[{role}]\n{content}\n")
        return self.complete("\n".join(parts), options=options)
