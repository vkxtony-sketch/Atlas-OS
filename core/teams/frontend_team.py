"""Atlas OS - Frontend Team."""
from __future__ import annotations

from core.teams.base import Team


class FrontendTeam(Team):
    name = "frontend"
    description = "React, UIs, accessibility, responsive layouts."
    responsibilities = ["User interface", "Accessibility", "Visual polish"]
    review_focus = [
        "ui", "react", "frontend", "page", "component", "responsive",
        "accessibility", "css", "layout", "ux",
    ]
    members = ["coder", "documentation_writer"]
