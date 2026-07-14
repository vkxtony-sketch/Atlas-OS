"""Atlas OS - team base class.

A ``Team`` is a named bag of agents plus a routing function. Teams
do NOT directly modify state; they return structured plans that the
``Executive`` is responsible for executing.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional


class Team:
    """Base team class."""

    name = "abstract"
    description = ""
    responsibilities: List[str] = []
    review_focus: List[str] = []
    members: List[str] = []  # agent role names from core.agents.registry

    def __init__(self, name: str = "", description: str = "") -> None:
        if name:
            self.name = name
        if description:
            self.description = description

    def accepts(self, goal: str) -> float:
        """Return confidence (0..1) that this team is the right owner.

        The default is a heuristic over keywords; teams override
        ``accepts`` for richer logic.
        """
        g = (goal or "").lower()
        score = 0.0
        for kw in self.review_focus:
            if kw in g:
                score += 0.25
        return min(1.0, score)

    def run_team(self, goal: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Hook for future expansion; safely default to "delegated"."""
        return {
            "team": self.name,
            "members": list(self.members),
            "status": "delegated",
            "note": "team.run_team() is a routing hook; executive applies members",
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "responsibilities": list(self.responsibilities),
            "review_focus": list(self.review_focus),
            "members": list(self.members),
        }
