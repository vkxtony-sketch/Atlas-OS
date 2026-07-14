"""Integration tests for permissions, audit, knowledge and integration hub."""
from __future__ import annotations

import os
import sys
import tempfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Default test policy is deny-everything (see conftest.py).
from core.permissions.gate import require_permission, reset_cache  # noqa: E402
from core.audit.log import audit, recent, audit_path  # noqa: E402
from core.config import reload_settings  # noqa: E402
from core.knowledge.search import search, rebuild_index  # noqa: E402


def test_permission_default_is_deny():
    os.environ["ATLAS_AUTO_DENY"] = "true"
    try:
        reset_cache()
        assert require_permission("git.push", {}) is False
        assert require_permission("anything.unknown", {}) is False
    finally:
        os.environ.pop("ATLAS_AUTO_DENY", None)


def test_permission_env_grant():
    os.environ.pop("ATLAS_AUTO_DENY", None)
    os.environ["ATLAS_ALLOW_GIT_PUSH"] = "true"
    try:
        reset_cache()
        assert require_permission("git.push", {}) is True
        assert require_permission("git.pull", {}) is False
    finally:
        os.environ.pop("ATLAS_ALLOW_GIT_PUSH", None)


def test_audit_writes_jsonl(monkeypatch):
    with tempfile.TemporaryDirectory() as tmp:
        monkeypatch.setenv("ATLAS_AUDIT_LOG_PATH", os.path.join(tmp, "audit.log"))
        reload_settings()
        audit("test.event", "denied", reason="unit-test")
        rows = recent(limit=10)
        assert any(r.get("action") == "test.event" for r in rows)
        assert os.path.exists(audit_path())


def test_knowledge_search_smoke(tmp_path):
    # Build a tiny knowledge directory and a marker file.
    notes = tmp_path / "notes"
    notes.mkdir()
    (notes / "intro.md").write_text(
        "Atlas OS is a local-first multi-agent operating system.\n\n"
        "It coordinates planner, researcher, coder, and a critic agent."
    )
    monkey_env_knowledge(tmp_path)
    rebuild_index()
    hits = search("multi-agent")
    assert hits, "expected at least one search hit"
    assert any("Atlas OS" in h["preview"] for h in hits)


def monkey_env_knowledge(path):
    os.environ["ATLAS_KNOWLEDGE_PATH"] = str(path)
    reload_settings()
