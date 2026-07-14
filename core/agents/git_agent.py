"""Atlas OS - Git Agent.

Designed *not* to touch disk by itself. Every side-effect action is gated
through ``core.permissions.gate.require_permission`` and recorded in the
audit log. Without that gate the agent returns a "prepared" record only.
"""
from __future__ import annotations

from typing import Any, Dict

from core.agents.base import BaseAgent


class GitAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__("git")

    def run(self, payload: Any) -> Dict[str, Any]:
        if not isinstance(payload, dict):
            payload = {"action": "status"}

        action = str(payload.get("action", "status"))

        # Actions that mutate history or talk to remotes require permission.
        if action in {"commit", "push", "create_branch", "open_pr"}:
            try:
                from core.permissions.gate import require_permission
                granted = require_permission(f"git.{action}", payload)
            except Exception as exc:  # noqa: BLE001
                return {"agent": self.name, "action": action,
                        "status": "failed", "reason": f"permission-gate-error: {exc}"}
            if not granted:
                return {"agent": self.name, "action": action,
                        "status": "denied",
                        "reason": "user did not approve the side-effect"}

        # Read-only status: always allowed.
        from core.integrations.connectors.git_cli import git_status
        return {
            "agent": self.name,
            "action": action,
            "result": git_status(),
            "status": "ok",
        }
