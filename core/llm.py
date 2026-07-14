"""Atlas OS - LLM facade.

Thin wrapper that resolves the configured ``LLMProvider`` and offers
``complete``/``chat`` helpers. Backed by ``core.llm_providers``.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from core.config import get_settings
from core.llm_providers import get_provider


class LLM:
    """Provider-aware language-model facade.

    The previous implementation was a hard-coded mock: it always returned a
    deterministic stub. This version honours ``ATLAS_LLM_PROVIDER`` and
    constructs the matching provider driver lazily on first use.
    """

    def __init__(self, provider: Optional[str] = None) -> None:
        self._provider_name = provider or get_settings().llm_provider
        self._provider = get_provider(self._provider_name)

    @property
    def provider(self) -> str:
        return self._provider.name

    @property
    def backend(self):
        return self._provider

    def complete(self, prompt: str, *, system: Optional[str] = None,
                 options: Optional[Dict[str, Any]] = None) -> str:
        return self._provider.complete(prompt, system=system, options=options)

    def chat(self, messages: List[Dict[str, str]],
             *, options: Optional[Dict[str, Any]] = None) -> str:
        return self._provider.chat(messages, options=options)

    # Backwards-compatible helper used by the legacy test scripts.
    def _mock_response(self, prompt: str) -> str:
        return self._provider.complete(prompt)
