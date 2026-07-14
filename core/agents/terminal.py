"""Atlas OS - Terminal Agent.

Hard-gated shell exec. The permission gate must approve every invocation
and every invocation is appended to the audit log. This is the boundary
to map onto a real sandbox.
"""
from __future__ import annotations

import shlex
import subprocess
from typing import Any, Dict, List

from core.agents.base import BaseAgent
from core.audit.log import audit


class TerminalAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__("terminal")

    def run(self, payload: Any) -> Dict[str, Any]:
        if not isinstance(payload, dict):
            payload = {"command": str(payload)}
        command = str(payload.get("command", "")).strip()

        if not command:
            return {"agent": self.name, "status": "skipped", "reason": "empty command"}

        try:
            from core.permissions.gate import require_permission
            granted = require_permission(
                "terminal.run",
                {"command": command, "argv": shlex.split(command)},
            )
        except Exception as exc:  # noqa: BLE001
            granted = False
            audit("terminal.run", "denied", reason=f"gate-error: {exc}")

        if not granted:
            return {"agent": self.name, "status": "denied",
                    "command": command,
                    "reason": "user did not approve the shell call"}

        audit("terminal.run", "granted", command=command)
        try:
            proc = subprocess.run(
                shlex.split(command),
                capture_output=True,
                text=True,
                timeout=15,
                check=False,
            )
        except Exception as exc:  # noqa: BLE001
            return {"agent": self.name, "status": "failed",
                    "command": command, "error": str(exc)}

        return {
            "agent": self.name,
            "status": "ok" if proc.returncode == 0 else "nonzero",
            "command": command,
            "returncode": proc.returncode,
            "stdout": proc.stdout[-2000:],
            "stderr": proc.stderr[-2000:],
        }
