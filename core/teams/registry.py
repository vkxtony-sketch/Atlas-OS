"""Atlas OS - team registry + goal router."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from core.teams.base import Team


class TeamRegistry:
    """Subscribe-and-route registry of ``Team`` instances.

    Used by the Executive to decide which team owns a goal. The
    registry is intentionally simple: each team returns an
    ``accepts(goal)`` confidence score and we pick the highest.
    """

    _items: Dict[str, Team] = {}

    @classmethod
    def register(cls, name: str, team: Team) -> None:
        cls._items[name] = team

    @classmethod
    def get(cls, name: str) -> Optional[Team]:
        return cls._items.get(name)

    @classmethod
    def all(cls) -> List[Team]:
        return [cls._items[k] for k in sorted(cls._items.keys())]

    @classmethod
    def list_names(cls) -> List[str]:
        return sorted(cls._items.keys())

    @classmethod
    def route_goal(cls, goal: str) -> Dict[str, Any]:
        if not cls._items:
            return {"primary": None, "secondary": None, "all_confidences": {}}
        scored = [(team, team.accepts(goal)) for team in cls._items.values()]
        scored.sort(key=lambda x: x[1], reverse=True)
        primary = scored[0][0] if scored else None
        secondary = scored[1][0] if len(scored) > 1 else None
        return {
            "primary": primary.name if primary else None,
            "primary_confidence": scored[0][1] if scored else 0.0,
            "secondary": secondary.name if secondary else None,
            "all_confidences": {t.name: s for t, s in scored},
            "members": primary.members if primary else [],
        }


def list_teams() -> List[str]:
    return TeamRegistry.list_names()
