"""Atlas OS - permission gate.

Designed so that any side-effect action has to opt in. The default
policy is *auto-deny* under ATLAS_AUTO_APPROVE=false; switch to true in
trusted dev environments.
"""
from core.permissions.gate import require_permission, reset_cache, allowed_actions

__all__ = ["require_permission", "reset_cache", "allowed_actions"]
