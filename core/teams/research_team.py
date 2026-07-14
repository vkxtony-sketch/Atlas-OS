"""Atlas OS - Research Team."""
from __future__ import annotations

from core.teams.base import Team


class ResearchTeam(Team):
    name = "research"
    description = "Official documentation, papers, GitHub projects, best practices."
    responsibilities = ["Find authoritative sources", "Summarise evidence"]
    review_focus = [
        "research", "investigate", "compare", "study", "paper", "arxiv",
        "official docs", "docs", "best practice", "industry",
    ]
    members = ["researcher", "knowledge"]
