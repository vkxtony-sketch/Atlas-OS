"""Atlas OS - Testing Team."""
from __future__ import annotations

from core.teams.base import Team


class TestingTeam(Team):
    name = "testing"
    description = "Unit, integration, e2e, edge cases."
    responsibilities = ["Author tests", "Generate edge cases", "Run regression"]
    review_focus = [
        "test", "pytest", "unittest", "coverage", "regression", "edge",
        "integration", "e2e", "smoke", "ci",
    ]
    members = ["qa_engineer"]
