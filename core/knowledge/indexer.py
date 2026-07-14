"""Atlas OS - chunker + indexer.

Walks a directory of supported files (md / py / txt / json / yml / toml),
chunks them into ~paragraph-shaped records, and persists them as JSON.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List


SUPPORTED_SUFFIXES = (".md", ".py", ".txt", ".json", ".yml", ".yaml", ".toml")
CHUNK_SIZE = 1200          # chars
CHUNK_OVERLAP = 120        # chars


@dataclass
class Chunk:
    chunk_id: str
    source: str
    start: int
    end: int
    text: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "source": self.source,
            "start": self.start,
            "end": self.end,
            "text": self.text,
        }


def _read_file(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception:
        return ""


def _chunk_one(path: str) -> List[Chunk]:
    body = _read_file(path)
    if not body:
        return []
    chunks: List[Chunk] = []
    cursor = 0
    while cursor < len(body):
        end = min(len(body), cursor + CHUNK_SIZE)
        # Try to break on whitespace for readability.
        if end < len(body):
            ws = body.rfind("\n\n", cursor, end)
            if ws > cursor + CHUNK_SIZE // 2:
                end = ws
        text = body[cursor:end].strip()
        if text:
            digest = hashlib.sha1(
                f"{path}:{cursor}:{end}".encode("utf-8")
            ).hexdigest()[:16]
            chunks.append(
                Chunk(
                    chunk_id=digest,
                    source=path,
                    start=cursor,
                    end=end,
                    text=text,
                )
            )
        cursor = max(end - CHUNK_OVERLAP, end)
    return chunks


def index_directory(path: str) -> List[Dict[str, Any]]:
    """Recursively index all supported files under ``path``."""
    out: List[Dict[str, Any]] = []
    for root, _dirs, files in os.walk(path):
        for f in files:
            if not f.endswith(SUPPORTED_SUFFIXES):
                continue
            full = os.path.join(root, f)
            for chunk in _chunk_one(full):
                out.append(chunk.to_dict())
    return out


_WORD = re.compile(r"[A-Za-z0-9_]+")


def tokenize(text: str) -> List[str]:
    return [w.lower() for w in _WORD.findall(text)]


def rebuild_index(path: str, out_path: str) -> int:
    """Build the chunk store and persist to ``out_path``. Returns count."""
    rows = index_directory(path)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)
    return len(rows)
