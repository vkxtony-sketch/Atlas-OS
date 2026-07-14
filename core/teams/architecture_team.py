"""Atlas OS - Software Architecture Team."""
from __future__ import annotations

from core.teams.base import Team


class ArchitectureTeam(Team):
    name = "architecture"
    description = "System design, scalability, APIs, folder structure, tech selection."
    responsibilities = [
        "Decide overall system shape",
        "Choose stack and component boundaries",
        "Pick deployment topology",
    ]
    review_focus = [
        "design", "architecture", "schema", "system", "stack", "topology",
        "module", "service", "monolith", "microservice",
    ]
    members = ["planner", "code_reviewer"]
