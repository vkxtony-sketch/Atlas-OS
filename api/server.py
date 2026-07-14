"""Atlas OS - FastAPI server.

Exposes the unified Executive contract:
* POST /run          — full goal execution, returns the contract dict.
* GET  /health       — process & config liveness/readiness.
* GET  /history      — task_history list, newest-first.
* GET  /memory/recent?limit=N — recent memory records.
* GET  /audit        — recent audit rows.
* GET  /teams        — registered teams + their capability list.
* GET  /agents       — known agent registry.

The previous implementation referenced ``executive.task_history`` and
``executive.memory.store`` (which didn't exist). Now those are real
methods on :class:`core.executive_ai.MultiAgentExecutive`.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from core.executive_ai import MultiAgentExecutive
from core.audit.log import recent as audit_recent
from core.agents.registry import list_agents, role_capabilities
from core.teams.registry import TeamRegistry
from core.config import get_settings


app = FastAPI(
    title="Atlas OS API",
    version="0.2.0",
    description=(
        "Local-first multi-agent orchestration. POST /run with a goal; the "
        "Executive AI plans, researches, codes, instructs reviewers, and "
        "consensus-merges the result."
    ),
)


class GoalRequest(BaseModel):
    goal: str = Field(..., min_length=1, description="User goal to execute.")


@app.on_event("startup")
def _startup() -> None:
    # Force team registry import so all eight teams are populated.
    import core.teams  # noqa: F401


@app.get("/")
def root() -> Dict[str, Any]:
    return {
        "name": "Atlas OS API",
        "version": "0.2.0",
        "endpoints": [
            "/run", "/health", "/history",
            "/memory/recent", "/audit",
            "/teams", "/agents",
        ],
    }


@app.get("/health")
def health() -> Dict[str, Any]:
    settings = get_settings()
    return {"status": "ok", "llm_provider": settings.llm_provider}


@app.post("/run")
def run_goal(req: GoalRequest) -> Dict[str, Any]:
    try:
        executive = MultiAgentExecutive()
        return executive.run_goal(req.goal)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/history")
def history() -> List[Dict[str, Any]]:
    execu = MultiAgentExecutive()
    return [t.to_dict() for t in execu.task_history]


@app.get("/memory/recent")
def memory_recent(limit: int = Query(20, ge=1, le=200)) -> List[Dict[str, Any]]:
    execu = MultiAgentExecutive()
    return execu.memory.get_recent(limit)


@app.get("/audit")
def audit_endpoint(limit: int = Query(100, ge=1, le=2000)) -> List[Dict[str, Any]]:
    return audit_recent(limit)


@app.get("/teams")
def teams_endpoint() -> List[Dict[str, Any]]:
    return [t.to_dict() for t in TeamRegistry.all()]


@app.get("/agents")
def agents_endpoint() -> Dict[str, Any]:
    return {
        "names": list_agents(),
        "capabilities": role_capabilities(),
    }


# ---------------------------------------------------------------------------
# Console entrypoint: ``uvicorn api.server:app --reload``
# ---------------------------------------------------------------------------

if __name__ == "__main__":  # pragma: no cover - convenience runner
    import uvicorn
    settings = get_settings()
    uvicorn.run(
        "api.server:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=False,
    )
