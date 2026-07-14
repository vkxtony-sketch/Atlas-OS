"""Atlas OS - plugin manager.

Lifecycle:

* Discover: walk each path in ``ATLAS_PLUGIN_DIRS``, pick up ``plugin.toml``
  or ``plugin.json``, parse to ``PluginManifest``.
* Load: import the manifest's ``entry`` (``module.path:callable``) and
  invoke ``callable(registry)`` where ``registry`` is a dict the loader
  passes through. The plugin can register agents, commands, or hooks.
* Hot reload: ``reload(name)`` re-imports after a manifest-driven
  refresh. Out of scope for the in-process sandbox; we only attempt a
  reload if ``ATLAS_HOT_RELOAD_PLUGINS=true``.

Subprocess sandbox policy:

* Each plugin runs in the *current* Python process (single-process model)
  with the same permission gate as everything else.
* Real cross-process sandboxing (seccomp / nsjail / firejail) is out of
  scope and should be wired in via ``core.security.sandbox`` (not
  implemented in this build).
"""
from __future__ import annotations

import importlib
import os
import traceback
from typing import Any, Dict, List, Optional

from core.audit.log import audit
from core.config import get_settings
from core.permissions.gate import require_permission
from core.plugins.manifest import PluginManifest, load_manifest


def _import_entry(entry: str):
    """Turn ``module.path:callable`` into the callable."""
    if ":" not in entry:
        raise ValueError(f"Plugin manifest 'entry' must be module:callable, got: {entry!r}")
    mod_name, _, attr = entry.partition(":")
    mod = importlib.import_module(mod_name)
    return getattr(mod, attr)


class PluginManager:
    def __init__(self) -> None:
        self._manifests: Dict[str, PluginManifest] = {}
        self._loaded: Dict[str, Any] = {}
        self._registry: Dict[str, Any] = {}

    # ---------- discovery ---------- #

    def discover(self) -> List[PluginManifest]:
        manifests: List[PluginManifest] = []
        for root in self._plugin_dirs():
            if not os.path.isdir(root):
                continue
            for entry in sorted(os.listdir(root)):
                full = os.path.join(root, entry)
                if not os.path.isdir(full):
                    continue
                for ext in ("plugin.toml", "plugin.json"):
                    candidate = os.path.join(full, ext)
                    if os.path.isfile(candidate):
                        try:
                            manifests.append(load_manifest(candidate))
                        except Exception as exc:  # noqa: BLE001
                            audit("plugin.discover", "failed",
                                  path=candidate, error=str(exc))
                        break
        return manifests

    def _plugin_dirs(self) -> List[str]:
        return list(self.settings.plugin_dirs)

    # ---------- load ---------- #

    def load_all(self) -> Dict[str, Any]:
        results: Dict[str, Any] = {}
        for manifest in self.discover():
            results[manifest.name] = self.load(manifest)
        return results

    def load(self, manifest: PluginManifest) -> Dict[str, Any]:
        if manifest.name in self._loaded:
            return self._loaded[manifest.name]

        # Permission check on every plugin load.
        granted = require_permission(
            "plugin.load",
            {"name": manifest.name, "permissions": manifest.permissions},
        )
        if not granted:
            audit("plugin.load", "denied", name=manifest.name)
            return {"name": manifest.name, "status": "denied"}

        # Make the plugin importable.
        if manifest.source_dir and manifest.source_dir not in os.sys.path:
            os.sys.path.insert(0, manifest.source_dir)

        try:
            entry = _import_entry(manifest.entry)
            entry(self._registry)
            self._manifests[manifest.name] = manifest
            self._loaded[manifest.name] = {
                "status": "loaded",
                "manifest": manifest.to_dict(),
            }
            audit("plugin.load", "granted", name=manifest.name)
        except Exception as exc:  # noqa: BLE001
            self._loaded[manifest.name] = {
                "status": "failed",
                "error": str(exc),
                "trace": traceback.format_exc(),
            }
            audit("plugin.load", "failed", name=manifest.name, error=str(exc))

        return self._loaded[manifest.name]

    # ---------- helpers ---------- #

    @property
    def settings(self):
        return get_settings()

    @property
    def registry(self) -> Dict[str, Any]:
        return self._registry

    def list_loaded(self) -> Dict[str, Any]:
        return dict(self._loaded)


plugin_manager = PluginManager()
