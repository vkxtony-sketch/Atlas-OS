"""Atlas OS - GitHub connector (`gh` CLI)."""
from __future__ import annotations

from typing import Any, Dict

from core.integrations.runner import run


def _args(*parts: str) -> list:
    return ["gh", *parts]


def is_available() -> bool:
    """Best-effort binary check; does not require permission."""
    import shutil
    return shutil.which("gh") is not None


def list_issues(repo: str = None, limit: int = 20) -> Dict[str, Any]:
    argv = _args("issue", "list", "--limit", str(limit), "--json",
                 "number,title,state,author,url")
    if repo:
        argv[1:1] = ["-R", repo]
    return run(argv)


def list_prs(repo: str = None, limit: int = 20) -> Dict[str, Any]:
    argv = _args("pr", "list", "--limit", str(limit), "--json",
                 "number,title,state,author,url")
    if repo:
        argv[1:1] = ["-R", repo]
    return run(argv)
