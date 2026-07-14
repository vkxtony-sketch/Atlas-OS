"""
Atlas OS - Python Tool (STUB-ONLY MODE)

SECURITY: this tool does NOT execute arbitrary user-supplied code by default.

In a real deployment a sandboxed subprocess (Docker / firejail / nsjail)
would execute code. Here we provide a structured "stub-only" reply so the
system can be reasonably exercised without an RCE path. To enable real
execution, set ATLAS_ALLOW_CODE_EXECUTION=true *and* wire in a real sandbox.

The previous implementation used ``exec()`` and was a literal RCE path.
Anyone who needs that capability must explicitly opt in below.
"""
from __future__ import annotations

import hashlib
import os
from typing import Any, Dict


class PythonTool:
    """
    Stub-only Python tool.

    Returns a deterministic, structured response describing what *would*
    happen if code were executed, but never executes user code.
    """

    name = "python"

    def __init__(self) -> None:
        self.allow_execution = (
            os.getenv("ATLAS_ALLOW_CODE_EXECUTION", "false").lower() == "true"
        )

    def run(self, code: str) -> Dict[str, Any]:
        # Compute a fingerprint so the caller can still tell repeats apart.
        digest = hashlib.sha256(code.encode("utf-8")).hexdigest()[:12]

        if not self.allow_execution:
            return {
                "status": "stub",
                "executed": False,
                "reason": (
                    "Execution disabled. PythonTool is in stub-only mode. "
                    "Set ATLAS_ALLOW_CODE_EXECUTION=true and wire a real "
                    "sandbox to actually run code."
                ),
                "code_sha256_12": digest,
                "line_count": code.count("\n") + 1,
                "char_count": len(code),
            }

        # If the user *explicitly* turned on execution, we still refuse
        # by default and instead return an error so the operator notices.
        # Real sandboxing is out of scope for this build.
        return {
            "status": "refused",
            "executed": False,
            "reason": (
                "ATLAS_ALLOW_CODE_EXECUTION=true but no real sandbox is "
                "configured. Refusing to exec() user input. "
                "Implement core/security/sandbox.py to enable."
            ),
            "code_sha256_12": digest,
        }
