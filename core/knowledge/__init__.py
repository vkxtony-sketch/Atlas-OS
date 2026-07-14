"""Atlas OS - knowledge subsystem.

Offline-friendly: chunking + TF-IDF over local files. Real semantic
search with vector embeddings is a documented extension point — it
is intentionally NOT wired in this build to keep the install footprint
small and the search transparent.
"""

from core.knowledge.search import search, index_directory, rebuild_index

__all__ = ["search", "index_directory", "rebuild_index"]
