"""
Atlas OS - LLM Interface Layer

This module abstracts language model access so agents can switch
between simulated mode and real AI providers (OpenAI, local LLMs, etc.).
"""

class LLM:
    def __init__(self, provider: str = "mock"):
        self.provider = provider

    def complete(self, prompt: str) -> str:
        if self.provider == "mock":
            return self._mock_response(prompt)

        return f"[LLM:{self.provider}] {prompt[:100]}"

    def _mock_response(self, prompt: str) -> str:
        return "Simulated LLM output based on prompt: " + prompt[:200]
