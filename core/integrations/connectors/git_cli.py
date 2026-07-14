"""Atlas OS - git CLI connector (read-only).

Wraps ``git status/diff/log`` via ``core.integrations.runner.run``.
Mutating commands (``git commit/push``) are intentionally left to the
``GitAgent`` which adds permission checking on top.
"""
from __future__ import annotations

from typing import Any, Dict, List

from core.integrations.runner import run


def _args(*parts: str) -> List[str]:
    return ["git", *parts]


def git_status(cwd: str = None) -> Dict[str, Any]:
    return run(_args("status", "--short", "--branch"), cwd=cwd)


def git_diff(cwd: str = None) -> Dict[str, Any]:
    return run(_args("diff", "--stat"), cwd=cwd)


def git_log(limit: int = 10, cwd: str = None) -> Dict[str, Any]:
    return run(_args("log", f"-n{limit}", "--oneline"), cwd=cwd)


def git_branch(cwd: str = None) -> Dict[str, Any]:
    return run(_args("branch", "--list"), cwd=cwd)
