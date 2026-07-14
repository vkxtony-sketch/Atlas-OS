"""Atlas OS - Knowledge Agent.

Routes queries to the offline knowledge index. The default backend is a
TF-IDF index built from files in ``ATLAS_KNOWLEDGE_PATH`` (markdown /
code / notes / PDFs-as-text). Semantic search is intentionally not wired
in this build: the indexer is small, transparent, and offline.
"""
from __future__ import annotations

from typing import Any, Dict

from core.agents.base import BaseAgent


class KnowledgeAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__("knowledge")

    def run(self, payload: Any) -> Dict[str, Any]:
        if isinstance(payload, dict):
            query = str(payload.get("query") or payload.get("goal") or "")
        else:
            query = str(payload)

        # Lazy import keeps the dev loop cheap when knowledge isn't used.
        from core.knowledge.search import search
        results = search(query, top_k=5)

        # Always loop the LLM through so agent memory stays populated.
        self.think(f"Knowledge query: {query}\nHits: {results}")

        return {
            "agent": self.name,
            "query": query,
            "results": results,
            "status": "served" if results else "no-hits",
        }
