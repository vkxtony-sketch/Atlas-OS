"""Atlas OS - append-only audit log.

Writes JSONL rows to the configured ``ATLAS_AUDIT_LOG_PATH``. The file
is never rotated, truncated, or rewritten by Atlas code itself. Read
back via ``recent()``.
"""
from __future__ import annotations

import json
import os
import time
from typing import Any, Dict, List, Optional

from core.config import get_settings


def audit_path() -> str:
    return get_settings().audit_log_path


def _ensure_parent(path: str) -> None:
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)


def audit(action: str, decision: str, **fields: Any) -> None:
    row = {
        "ts": time.time(),
        "action": action,
        "decision": decision,
        **fields,
    }
    path = audit_path()
    _ensure_parent(path)
    # Atomic append; ignore errors so audit never breaks the caller.
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    except Exception:
        pass


def recent(limit: int = 200) -> List[Dict[str, Any]]:
    path = audit_path()
    if not os.path.exists(path):
        return []
    rows: List[Dict[str, Any]] = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            tail = f.readlines()[-limit:]
    except Exception:
        return []
    for line in tail:
        try:
            rows.append(json.loads(line))
        except Exception:
            continue
    return rows


# Best-effort file lock import; ignored if fcntl unavailable (Windows).
try:  # noqa: E402
    import fcntl  # type: ignore
except Exception:  # pragma: no cover - non-POSIX
    fcntl = None  # type: ignore
