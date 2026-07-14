"""Atlas OS - LLM provider bridge.

Provides a tiny ``LLMProvider`` protocol and built-in drivers:

* ``mock``     — deterministic stub (default).
* ``template`` — prompt-templated deterministic output (also offline).
* ``http``     — POST to OpenAI-compatible HTTP endpoint (e.g. llama.cpp
  server, lm-studio, vLLM, OpenAI).
* ``echo``     — pass-through (used in tests).

Real local model loaders (llama-cpp-python, transformers, mlx) are out of
scope for this build. ``http`` is the boundary a self-hosted model server
can plug into.
"""
from __future__ import annotations

from typing import Dict, Type

from core.llm_providers.base import LLMProvider
from core.llm_providers.mock_provider import MockProvider
from core.llm_providers.template_provider import TemplateProvider
from core.llm_providers.http_provider import HttpProvider
from core.llm_providers.echo_provider import EchoProvider

_REGISTRY: Dict[str, Type[LLMProvider]] = {
    "mock": MockProvider,
    "template": TemplateProvider,
    "http": HttpProvider,
    "echo": EchoProvider,
}


def get_provider(name: str) -> LLMProvider:
    name = (name or "mock").strip().lower()
    if name not in _REGISTRY:
        raise ValueError(
            f"Unknown LLM provider '{name}'. Known: {sorted(_REGISTRY.keys())}"
        )
    return _REGISTRY[name]()


def list_providers() -> list[str]:
    return sorted(_REGISTRY.keys())


__all__ = ["LLMProvider", "get_provider", "list_providers"]
