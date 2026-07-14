"""Atlas OS - centralized runtime configuration.

This module is the single source of truth for runtime configuration. Every
other module that needs a knob should read it from ``AtlasSettings`` instead
of touching ``os.environ`` directly so we can test deterministically.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import List, Optional


def _env(name: str, default: str) -> str:
    return os.getenv(name, default)


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except (TypeError, ValueError):
        return default


def _env_bool(name: str, default: bool) -> bool:
    return os.getenv(name, str(default)).lower() in {"1", "true", "yes", "on"}


def _env_list(name: str, default: Optional[List[str]] = None) -> List[str]:
    raw = os.getenv(name)
    if not raw:
        return default or []
    return [item.strip() for item in raw.split(",") if item.strip()]


@dataclass
class AtlasSettings:
    """Process-wide settings; construct once at startup."""

    # LLM provider selection.
    llm_provider: str = field(default_factory=lambda: _env("ATLAS_LLM_PROVIDER", "mock"))

    # How the orchestrator should chase consensus.
    consensus_passes: int = field(default_factory=lambda: _env_int("ATLAS_CONSENSUS_PASSES", 1))
    review_target_score: int = field(default_factory=lambda: _env_int("ATLAS_REVIEW_TARGET_SCORE", 70))

    # Autonomous loop bounds.
    autonomous_interval: float = field(
        default_factory=lambda: float(_env("ATLAS_AUTONOMOUS_INTERVAL", "5"))
    )
    autonomous_max_cycles: int = field(
        default_factory=lambda: _env_int("ATLAS_AUTONOMOUS_MAX_CYCLES", 10)
    )

    # Web tool.
    web_tool_mode: str = field(default_factory=lambda: _env("ATLAS_WEB_TOOL_MODE", "mock"))
    web_search_endpoint: str = field(default_factory=lambda: _env("ATLAS_WEB_SEARCH_ENDPOINT", ""))

    # FastAPI server.
    api_host: str = field(default_factory=lambda: _env("ATLAS_API_HOST", "127.0.0.1"))
    api_port: int = field(default_factory=lambda: _env_int("ATLAS_API_PORT", 8000))

    # Security / permissions.
    allow_code_execution: bool = field(
        default_factory=lambda: _env_bool("ATLAS_ALLOW_CODE_EXECUTION", False)
    )
    require_permission_for: List[str] = field(
        default_factory=lambda: _env_list(
            "ATLAS_REQUIRE_PERMISSION_FOR",
            ["git.commit", "git.push", "deploy.run", "terminal.run"],
        )
    )
    audit_log_path: str = field(
        default_factory=lambda: _env("ATLAS_AUDIT_LOG_PATH", "atlas_audit.log")
    )

    # Optional encryption at rest.
    enable_encrypted_memory: bool = field(
        default_factory=lambda: _env_bool("ATLAS_ENABLE_ENCRYPTED_MEMORY", False)
    )

    # Plugins.
    plugin_dirs: List[str] = field(
        default_factory=lambda: _env_list("ATLAS_PLUGIN_DIRS", ["plugins"])
    )

    # Memory paths.
    memory_path: str = field(default_factory=lambda: _env("ATLAS_MEMORY_PATH", "atlas_memory.json"))
    shared_memory_path: str = field(
        default_factory=lambda: _env("ATLAS_SHARED_MEMORY_PATH", "atlas_shared_memory.json")
    )

    # Knowledge.
    knowledge_path: str = field(
        default_factory=lambda: _env("ATLAS_KNOWLEDGE_PATH", "atlas_knowledge")
    )


_settings: Optional[AtlasSettings] = None


def get_settings() -> AtlasSettings:
    """Get (or create) the process-wide ``AtlasSettings`` singleton."""
    global _settings
    if _settings is None:
        _settings = AtlasSettings()
    return _settings


def reload_settings() -> AtlasSettings:
    """Force re-read env vars into a new ``AtlasSettings``."""
    global _settings
    _settings = AtlasSettings()
    return _settings
