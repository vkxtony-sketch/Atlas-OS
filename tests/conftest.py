"""Shared pytest fixtures.

By default we run with auto-approve OFF and auto-deny OFF so per-test
settings can take effect. Tests that need a deny-by-default posture
manage it inline.
"""
from __future__ import annotations

import os

# Wipe any pre-existing permissive state.
for k in ("ATLAS_AUTO_APPROVE", "ATLAS_AUTO_DENY"):
    os.environ.pop(k, None)

# Default behaviour for the test suite: explicit grants required.
os.environ.setdefault("ATLAS_AUTO_APPROVE", "false")
