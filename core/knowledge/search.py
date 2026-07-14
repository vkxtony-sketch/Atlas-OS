"""Atlas OS - knowledge search.

Real offline TF-IDF + cosine similarity over the chunk index built by
``core.knowledge.indexer``. No embeddings, no network.
"""
from __future__ import annotations

import json
import math
import os
from collections import Counter
from typing import Any, Dict, List, Optional

from core.config import get_settings
from core.knowledge.indexer import index_directory, tokenize


def _index_path() -> str:
    return os.path.join(get_settings().knowledge_path, "chunks.json")


def rebuild_index() -> int:
    """Rebuild the chunk store from the configured knowledge path."""
    from core.knowledge.indexer import rebuild_index as _rb
    os.makedirs(get_settings().knowledge_path, exist_ok=True)
    return _rb(get_settings().knowledge_path, _index_path())


def _load_index() -> List[Dict[str, Any]]:
    path = _index_path()
    if not os.path.exists(path):
        # On-demand materialisation from source if empty.
        os.makedirs(get_settings().knowledge_path, exist_ok=True)
        rebuild_index()
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def _tfidf_vector(text: str, df: Dict[str, int], n_docs: int) -> Dict[str, float]:
    counts = Counter(tokenize(text))
    if not counts:
        return {}
    total = sum(counts.values())
    vec: Dict[str, float] = {}
    for term, c in counts.items():
        tf = c / total
        idf = math.log((1 + n_docs) / (1 + (df.get(term, 0)))) + 1.0
        vec[term] = tf * idf
    return vec


def _cosine(a: Dict[str, float], b: Dict[str, float]) -> float:
    if not a or not b:
        return 0.0
    # Cosine over shared term keys.
    keys = set(a.keys()) & set(b.keys())
    dot = sum(a[k] * b[k] for k in keys)
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def search(query: str, *, top_k: int = 5) -> List[Dict[str, Any]]:
    """Return the top-k most similar chunks to ``query``."""
    query = (query or "").strip()
    if not query:
        return []

    rows = _load_index()
    if not rows:
        return []

    df: Dict[str, int] = {}
    for r in rows:
        for term in set(tokenize(r.get("text", ""))):
            df[term] = df.get(term, 0) + 1
    n_docs = len(rows)

    qv = _tfidf_vector(query, df, n_docs)
    scored: List[tuple[float, Dict[str, Any]]] = []
    for r in rows:
        rv = _tfidf_vector(r.get("text", ""), df, n_docs)
        s = _cosine(qv, rv)
        if s > 0:
            scored.append((s, r))
    scored.sort(key=lambda x: x[0], reverse=True)

    return [
        {
            "score": round(s, 4),
            "source": r.get("source"),
            "preview": (r.get("text") or "")[:240],
        }
        for s, r in scored[:top_k]
    ]
