"""Atlas OS sample plugin entry point.

A plugin ``register(registry)`` registers capabilities on the global
plugin registry. This example exposes a single ``summarise()`` callable
that returns a dict describing the local git status.
"""
from __future__ import annotations

from typing import Any, Dict


def register(registry: Dict[str, Any]) -> None:
    def summarise(cwd: str = None) -> Dict[str, Any]:
        # Lazy-import so the plugin doesn't load connectors unless used.
        from core.integrations.connectors.git_cli import (
            git_status, git_log, git_branch,
        )
        return {
            "status": git_status(cwd),
            "log": git_log(limit=5, cwd=cwd),
            "branches": git_branch(cwd=cwd),
        }
    registry["git_summary.summarise"] = summarise
