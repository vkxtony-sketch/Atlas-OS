"""Atlas OS - Documentation Team."""
from __future__ import annotations

from core.teams.base import Team


class DocumentationTeam(Team):
    name = "documentation"
    description = "READMEs, API documentation, user guides, developer docs."
    responsibilities = ["Keep docs in sync with code", "Write API references"]
    review_focus = [
        "readme", "doc", "documentation", "api reference", "manual",
        "guide", "spec", "comment", "inline doc",
    ]
    members = ["documentation_writer"]
