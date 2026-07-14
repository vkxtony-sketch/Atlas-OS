"""Atlas OS - plugin subsystem.

Constraints:

* Discover via a manifest (``plugin.toml`` or ``plugin.json``).
* Load classes ONLY through a stable contract (``register(registry)``).
* Auto-loaded on import OR explicitly via ``PluginManager.load_all``.
* Subject to the same permission gate + audit log as everything else.
"""

from core.plugins.manifest import PluginManifest, load_manifest
from core.plugins.manager import PluginManager, plugin_manager

__all__ = [
    "PluginManifest",
    "load_manifest",
    "PluginManager",
    "plugin_manager",
]
