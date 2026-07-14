"""Atlas OS - Backend Team."""
from __future__ import annotations

from core.teams.base import Team


class BackendTeam(Team):
    name = "backend"
    description = "APIs, databases, authentication, business logic."
    responsibilities = ["Implement the server side", "Model data", "Wire auth"]
    review_focus = [
        "api", "endpoint", "database", "db", "migration", "auth",
        "server", "sql", "orm", "model", "controller", "route", "schema",
    ]
    members = ["coder", "code_reviewer", "qa_engineer"]
