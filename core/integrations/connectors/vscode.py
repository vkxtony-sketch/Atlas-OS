"""Atlas OS - VS Code connector (open a file/folder)."""
from __future__ import annotations

from typing import Any, Dict

from core.integrations.runner import run


def _args(*parts: str) -> list:
    return ["code", *parts]


def open_path(path: str) -> Dict[str, Any]:
    """Open a file/folder/workspace in VS Code."""
    return run(_args(path))
