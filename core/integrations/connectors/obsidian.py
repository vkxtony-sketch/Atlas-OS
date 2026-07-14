"""Atlas OS - Obsidian connector (read a vault folder).

Same offline-first approach as the Notion connector: read the vault
directly as files rather than going through any Obsidian API.
"""
from __future__ import annotations

import os
from typing import Any, Dict, List


def list_notes(vault: str) -> Dict[str, Any]:
    if not os.path.isdir(vault):
        return {"ok": False, "error": "not-a-folder", "vault": vault}
    notes: List[str] = []
    for root, _dirs, files in os.walk(vault):
        if any(part.startswith(".") for part in root.split(os.sep)):
            continue
        for f in files:
            if f.endswith(".md"):
                notes.append(os.path.join(root, f))
    return {"ok": True, "vault": vault, "notes": notes[:1000]}


def index_vault(vault: str) -> Dict[str, Any]:
    """Cross-reference [[wiki-links]] inside the vault."""
    listing = list_notes(vault)
    if not listing.get("ok"):
        return listing
    edges: Dict[str, List[str]] = {}
    for path in listing["notes"]:
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception:
            continue
        name = os.path.splitext(os.path.basename(path))[0]
        edges[name] = []
        i = 0
        while True:
            idx = content.find("[[", i)
            if idx < 0:
                break
            end = content.find("]]", idx + 2)
            if end < 0:
                break
            link = content[idx + 2:end].split("|", 1)[0].strip()
            edges[name].append(link)
            i = end + 2
    return {"ok": True, "vault": vault, "edges": edges}
