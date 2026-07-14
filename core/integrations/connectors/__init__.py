"""Atlas OS - integration connectors.

Each module wraps a single external tool in a thin Atlas-aware facade:
* ``git_cli``       — git status/diff/log (read-only).
* ``github``        — `gh` CLI: issues, PRs.
* ``docker``        — `docker` CLI: ps, images.
* ``vscode``        — `code` CLI to open a path.
* ``notion``        — reads a Notion-export markdown folder.
* ``obsidian``      — reads an Obsidian vault folder.

All connectors go through ``core.integrations.runner.run``.
"""

from core.integrations.connectors import (
    git_cli, github, docker as docker_connector,
    vscode, notion, obsidian,
)

__all__ = [
    "git_cli", "github", "docker_connector",
    "vscode", "notion", "obsidian",
]
