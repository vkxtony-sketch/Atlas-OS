"""Atlas OS - Docker connector (`docker` CLI).

Read-only operations (`ps`, `images`) by default. Mutating commands
(stop, rm, run) are intentionally NOT wrapped here — those belong in
the Deployment agent behind an explicit permission grant.
"""
from __future__ import annotations

from typing import Any, Dict

from core.integrations.runner import run


def _args(*parts: str) -> list:
    return ["docker", *parts]


def list_containers(all_: bool = True) -> Dict[str, Any]:
    argv = _args("ps", "--format", "{{.ID}}\t{{.Image}}\t{{.Status}}\t{{.Names}}")
    if all_:
        argv.append("--all")
    return run(argv)


def list_images() -> Dict[str, Any]:
    return run(_args("images", "--format", "{{.Repository}}\t{{.Tag}}\t{{.ID}}"))
