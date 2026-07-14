"""Atlas OS - subprocess runner with allow-list + audit.

Real subprocess calls outside the Python process happen here. Each call:

* Checks the allow-list (``allow_command``).
* Asks the permission gate.
* Logs the audit row.
* Returns a structured result dict including stdout/stderr (truncated).
"""
from __future__ import annotations

import os
import shlex
import shutil
import subprocess
from typing import Any, Dict, List

from core.audit.log import audit


# Default allow-list. Extend via env ATLAS_ALLOW_BIN="gh,docker,code".
_DEFAULT_BIN_ALLOW: List[str] = [
    "gh", "git", "docker", "podman", "code", "cursor", "obsidian",
    "ls", "cat", "head", "tail", "wc", "jq", "rg", "grep",
    "true", "false", "echo",
]


def allow_command() -> List[str]:
    extra = os.getenv("ATLAS_ALLOW_BIN", "")
    out = list(_DEFAULT_BIN_ALLOW)
    if extra:
        out.extend(s.strip() for s in extra.split(",") if s.strip())
    return sorted(set(out))


def _binary_exists(binary: str) -> bool:
    return shutil.which(binary) is not None


def can_run(argv: List[str]) -> bool:
    """True iff the first arg is on the allow-list and present on disk."""
    if not argv:
        return False
    head = argv[0]
    if head not in allow_command():
        return False
    return _binary_exists(head)


def run(argv: List[str], *, cwd: str = None, env: Dict[str, str] = None,
        timeout: float = 30.0) -> Dict[str, Any]:
    """Run an allow-listed subprocess; return a structured result dict."""
    if not can_run(argv):
        return {"ok": False, "error": "command-blocked-or-missing", "argv": argv}

    try:
        from core.permissions.gate import require_permission
        granted = require_permission("terminal.run",
                                     {"argv": argv, "cwd": cwd})
    except Exception:
        granted = False
    if not granted:
        return {"ok": False, "error": "permission-denied", "argv": argv}

    audit("terminal.run", "granted", argv=argv, cwd=cwd)

    try:
        proc = subprocess.run(
            argv,
            cwd=cwd,
            env={**os.environ, **(env or {})},
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": str(exc), "argv": argv}

    return {
        "ok": proc.returncode == 0,
        "returncode": proc.returncode,
        "stdout": proc.stdout[-4000:],
        "stderr": proc.stderr[-4000:],
        "argv": argv,
    }
