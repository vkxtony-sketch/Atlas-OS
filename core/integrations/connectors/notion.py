"""Atlas OS - Notion connector (read markdown export folder).

This connector is *offline* by design — Notion's API requires OAuth,
which is out of scope for this build. Users who want to use Notion
content as knowledge can export their workspace to a folder of
Markdown files via Notion's web export, then point this connector at
that folder.
"""
from __future__ import annotations

import os
from typing import Any, Dict, List


def list_markdown_files(folder: str) -> Dict[str, Any]:
    if not os.path.isdir(folder):
        return {"ok": False, "error": "not-a-folder", "folder": folder}
    out: List[str] = []
    for root, _dirs, files in os.walk(folder):
        for f in files:
            if f.endswith(".md"):
                out.append(os.path.join(root, f))
    return {"ok": True, "folder": folder, "files": out[:500]}


def read_markdown(folder: str, file_name: str) -> Dict[str, Any]:
    full = os.path.join(folder, file_name)
    if not os.path.isfile(full):
        return {"ok": False, "error": "not-found", "path": full}
    try:
        with open(full, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": str(exc), "path": full}
    return {"ok": True, "path": full, "content": content[:8000]}
