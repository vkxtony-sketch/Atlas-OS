"""Atlas OS - plugin manifest.

A plugin is detected by a manifest file (``.toml`` preferred, ``.json``
fallback):

    [plugin]
    name = "git_summary"
    version = "0.1.0"
    entry = "git_summary.plugin:register"
    description = "..."
    permissions = ["git.commit"]

Loading happens in ``core.plugins.manager``. This module only parses
manifests.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class PluginManifest:
    name: str
    version: str
    entry: str
    description: str = ""
    permissions: List[str] = field(default_factory=list)
    source_dir: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "entry": self.entry,
            "description": self.description,
            "permissions": list(self.permissions),
            "source_dir": self.source_dir,
        }


def _read_toml(path: str) -> Dict[str, Any]:
    """Tiny pure-stdlib TOML reader for the small subset we need.

    Falls back to JSON if the file isn't parseable as TOML. We intentionally
    avoid pulling in ``tomli``/``tomllib``.

    Expected structure::

        [plugin]
        name = "..."
        ...
    """
    out: Dict[str, Any] = {}
    section: Optional[str] = None
    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.split("#", 1)[0].strip()
            if not line:
                continue
            if line.startswith("[") and line.endswith("]"):
                section = line[1:-1].strip()
                out.setdefault(section, {})
                continue
            if "=" in line:
                k, _, v = line.partition("=")
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                target = out[section] if section else out
                target[k] = v
    return out


def load_manifest(path: str) -> PluginManifest:
    raw: Dict[str, Any]
    if path.endswith(".toml"):
        raw = _read_toml(path).get("plugin", {})
    elif path.endswith(".json"):
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f).get("plugin", {})
    else:
        raise ValueError(f"unsupported manifest extension: {path}")

    return PluginManifest(
        name=str(raw.get("name", os.path.basename(os.path.dirname(path)))),
        version=str(raw.get("version", "0.0.0")),
        entry=str(raw.get("entry", "")),
        description=str(raw.get("description", "")),
        permissions=[str(p) for p in raw.get("permissions", []) or []],
        source_dir=os.path.dirname(os.path.abspath(path)),
    )
