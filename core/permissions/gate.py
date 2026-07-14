"""Atlas OS - permission gate.

A single function ``require_permission(action, payload) -> bool`` that
every side-effecting agent calls before performing the action.

Behavior is driven by env vars:

* ``ATLAS_AUTO_APPROVE=true``  — grants everything (dev convenience).
* ``ATLAS_AUTO_DENY=true``     — denies everything (paranoid mode).
* ``ATLAS_ALLOW_<UPPER>=true`` — grant a single ``action`` selectively,
  e.g. ``ATLAS_ALLOW_GIT_PUSH=true`` grants ``git.push``.

Anything else falls back to "deny + record in audit log".

This module never raises; failures return ``False`` so callers can
treat it as advisory (then audit-visible).
"""
from __future__ import annotations

import os
from typing import Any, Dict, List, Set

from core.audit.log import audit


_APPROVED: Set[str] = set()


def _is_auto_approve() -> bool:
    return os.getenv("ATLAS_AUTO_APPROVE", "false").lower() in {"1", "true", "yes", "on"}


def _is_auto_deny() -> bool:
    return os.getenv("ATLAS_AUTO_DENY", "false").lower() in {"1", "true", "yes", "on"}


def _env_grants_for(action: str) -> bool:
    key = "ATLAS_ALLOW_" + action.upper().replace(".", "_")
    return os.getenv(key, "false").lower() in {"1", "true", "yes", "on"}


def reset_cache() -> None:
    """Reset any cached approval decisions (per-process)."""
    _APPROVED.clear()


def allowed_actions() -> List[str]:
    """List of actions currently auto-approved (cosmetic, for UI)."""
    return sorted(_APPROVED)


def require_permission(action: str, payload: Dict[str, Any] | None = None) -> bool:
    payload = payload or {}
    if _is_auto_deny():
        audit(action, "denied", reason="auto-deny")
        return False
    if _is_auto_approve():
        _APPROVED.add(action)
        audit(action, "granted", reason="auto-approve")
        return True
    if _env_grants_for(action):
        _APPROVED.add(action)
        audit(action, "granted", reason="env-grant")
        return True
    audit(action, "denied", reason="no-grant")
    return False
