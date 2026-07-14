"""Atlas OS - File Agent.

Read-mostly utilities for projects. Writes (`mkdir`, `write`) require
permission. This deliberately does not delete or move files; renames go
through the TerminalAgent's gate instead.
"""
from __future__ import annotations

import os
from typing import Any, Dict, List

from core.agents.base import BaseAgent
from core.audit.log import audit


class FileAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__("file")

    def run(self, payload: Any) -> Dict[str, Any]:
        if not isinstance(payload, dict):
            payload = {"action": "list", "path": "."}
        action = str(payload.get("action", "list"))
        path = str(payload.get("path", "."))

        if action == "list":
            return self._list(path)
        if action == "search":
            return self._search(path, str(payload.get("needle", "")))
        if action == "mkdir":
            return self._mkdir(path)
        if action == "write":
            return self._write(path, str(payload.get("content", "")))

        return {"agent": self.name, "status": "unknown-action", "action": action}

    # ------------------------------ read ------------------------------ #

    def _list(self, path: str) -> Dict[str, Any]:
        if not os.path.isdir(path):
            return {"agent": self.name, "status": "not-a-dir", "path": path}
        names: List[str] = []
        for entry in sorted(os.listdir(path)):
            full = os.path.join(path, entry)
            kind = "d" if os.path.isdir(full) else "f"
            names.append(f"{kind} {entry}")
        return {"agent": self.name, "status": "ok",
                "path": path, "entries": names[:200]}

    def _search(self, path: str, needle: str) -> Dict[str, Any]:
        needle = needle.strip()
        if not needle:
            return {"agent": self.name, "status": "empty-needle"}
        hits: List[Dict[str, str]] = []
        for root, _dirs, files in os.walk(path):
            for f in files:
                if not f.endswith((".py", ".md", ".txt", ".json", ".yml", ".yaml", ".toml")):
                    continue
                full = os.path.join(root, f)
                try:
                    with open(full, "r", encoding="utf-8", errors="ignore") as fh:
                        content = fh.read()
                except Exception:
                    continue
                if needle in content:
                    hits.append({"file": full, "preview": content[:160]})
                    if len(hits) >= 25:
                        break
            if len(hits) >= 25:
                break
        return {"agent": self.name, "status": "ok",
                "needle": needle, "hits": hits}

    # ----------------------------- mutate ----------------------------- #

    def _mkdir(self, path: str) -> Dict[str, Any]:
        try:
            from core.permissions.gate import require_permission
            granted = require_permission("file.mkdir", {"path": path})
        except Exception:
            granted = False
        if not granted:
            return {"agent": self.name, "status": "denied", "action": "mkdir"}
        audit("file.mkdir", "granted", path=path)
        try:
            os.makedirs(path, exist_ok=True)
        except Exception as exc:  # noqa: BLE001
            return {"agent": self.name, "status": "failed", "error": str(exc)}
        return {"agent": self.name, "status": "ok", "action": "mkdir", "path": path}

    def _write(self, path: str, content: str) -> Dict[str, Any]:
        try:
            from core.permissions.gate import require_permission
            granted = require_permission("file.write", {"path": path, "bytes": len(content)})
        except Exception:
            granted = False
        if not granted:
            return {"agent": self.name, "status": "denied", "action": "write"}
        audit("file.write", "granted", path=path, bytes=len(content))
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as exc:  # noqa: BLE001
            return {"agent": self.name, "status": "failed", "error": str(exc)}
        return {"agent": self.name, "status": "ok", "action": "write",
                "path": path, "bytes": len(content)}
