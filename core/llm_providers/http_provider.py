"""Atlas OS - HTTP LLM provider.

POSTs to an OpenAI-compatible ``/v1/chat/completions`` endpoint. This is
the *integration boundary* for self-hosted (llama.cpp server, lm-studio,
vLLM, Ollama with OpenAI compat shim) or managed providers (OpenAI,
Together, Groq) — none of those are wired in directly; you supply the URL.

Configuration (env):

* ``ATLAS_LLM_HTTP_URL``  — e.g. ``http://127.0.0.1:8080/v1/chat/completions``
* ``ATLAS_LLM_HTTP_MODEL`` — model name to send in the request
* ``ATLAS_LLM_HTTP_TOKEN`` — optional bearer token
* ``ATLAS_LLM_HTTP_TIMEOUT`` — seconds, default 30

If the URL is not set the provider returns the same shape as ``MockProvider``
so callers can still exercise downstream code in dev mode.
"""
from __future__ import annotations

import hashlib
import json
import os
from typing import Any, Dict, List, Optional

from core.llm_providers.base import Capability, LLMProvider


def _env(name: str, default: str = "") -> str:
    return os.getenv(name, default)


class HttpProvider(LLMProvider):
    name = "http"

    def __init__(self) -> None:
        self.url = _env("ATLAS_LLM_HTTP_URL", "")
        self.model = _env("ATLAS_LLM_HTTP_MODEL", "atlas-local")
        self.token = _env("ATLAS_LLM_HTTP_TOKEN", "")
        try:
            self.timeout = float(_env("ATLAS_LLM_HTTP_TIMEOUT", "30"))
        except ValueError:
            self.timeout = 30.0

    def capabilities(self) -> Capability:
        return Capability(streaming=False, tool_use=False, json_mode=True,
                          max_context_chars=32_000)

    def chat(self, messages: List[Dict[str, str]],
             *, options: Optional[Dict[str, Any]] = None) -> str:
        if not self.url:
            # Offline-safe fallback.
            digest = hashlib.sha256(repr(messages).encode("utf-8")).hexdigest()[:8]
            return (
                f"[http-llm:offline:{digest}] ATLAS_LLM_HTTP_URL not set; "
                "returning deterministic offline stub."
            )

        # Lazy import: httpx is only required when the user actually configures
        # the http provider. Keeps the dev/test path light.
        import httpx  # type: ignore

        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": float((options or {}).get("temperature", 0.2)),
        }
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.post(self.url, headers=headers, content=json.dumps(payload))
                resp.raise_for_status()
                data = resp.json()
        except Exception as exc:  # noqa: BLE001
            return f"[http-llm:error] {type(exc).__name__}: {exc}"

        try:
            return data["choices"][0]["message"]["content"]
        except Exception:
            return f"[http-llm:bad-shape] {json.dumps(data)[:400]}"
