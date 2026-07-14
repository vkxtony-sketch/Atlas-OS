"""Atlas OS - integrations.

Subprocess-mediated integration hub. Every connector that touches the
outside world goes through ``core.integrations.runner.run``, which is
itself gated by the permission system and audited.
"""
from core.integrations.runner import run, allow_command, can_run

__all__ = ["run", "allow_command", "can_run"]
