"""Atlas OS - Executive AI.

Sole entry point that the CLI / API / Dashboard use. Builds a result dict
that satisfies the contract ``main.py`` reads::

    result["planner"]    -> planning output (dict)
    result["research"]   -> research output (dict|None)
    result["coding"]     -> coding output (dict|None)
    result["critic"]     -> critic output (dict)
    result["consensus"]  -> consensus output (dict)
    result["status"]     -> "complete" | "needs_revision" | "empty"

It also exposes ``.memory`` (a ``MemoryStore``) and ``.task_history``
(list of ``Task``) which the previous API/UI code expected but were never
defined.

The Executive will, in order:
1.  Plan the goal with ``PlannerAgent``.
2.  Optionally elicit research with ``ResearchAgent`` (only when needed).
3.  Generate code-level synthesis with ``CoderAgent``.
4.  Score with ``CriticAgent``.
5.  Until ``review_target_score`` is reached or ``consensus_passes`` elapse,
    re-run with critic feedback driving the next pass.
6.  Aggregate with ``ConsensusEngine`` into a single accepted answer.

When ``ATLAS_USE_TEAMS`` is ``true`` the executive first routes the goal
through the ``TeamRegistry`` so org-style team delegation can take over.
"""
from __future__ import annotations

import time
import uuid
from typing import Any, Dict, List, Optional

from core.agents.planner import PlannerAgent
from core.agents.researcher import ResearchAgent
from core.agents.coder import CoderAgent
from core.agents.critic import CriticAgent
from core.consensus_engine import ConsensusEngine
from core.config import get_settings
from core.memory.store import MemoryStore
from core.task import Task


class MultiAgentExecutive:
    """Top-level multi-agent orchestrator.

    Public surface intentionally simple and stable. Every entry point
    (CLI, FastAPI, Streamlit) consumes the same ``run_goal`` shape.
    """

    def __init__(
        self,
        *,
        planner: Optional[PlannerAgent] = None,
        researcher: Optional[ResearchAgent] = None,
        coder: Optional[CoderAgent] = None,
        critic: Optional[CriticAgent] = None,
        consensus: Optional[ConsensusEngine] = None,
    ) -> None:
        self.planner = planner or PlannerAgent()
        self.researcher = researcher or ResearchAgent()
        self.coder = coder or CoderAgent()
        self.critic = critic or CriticAgent()
        self.consensus = consensus or ConsensusEngine()

        self.settings = get_settings()
        self.memory = MemoryStore(path=self.settings.memory_path)

        self.task_queue: List[Task] = []
        self.task_history: List[Task] = []

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def run_goal(self, goal: str) -> Dict[str, Any]:
        """Execute a goal end-to-end and return the contract dict.

        Always returns ALL six keys so legacy callers cannot crash on
        ``KeyError``.
        """
        if not (goal or "").strip():
            return self._empty_result(reason="empty goal")

        task = self._make_task(goal)
        self.task_queue.append(task)
        task.mark_running()

        # Optional team-routing hook: if enabled, let the team registry
        # dispatch the goal instead of the default flow.
        team_record: Optional[Dict[str, Any]] = None
        if self.settings.llm_provider:
            # Lazy import so importing this module doesn't require
            # the team registry to be fully wired at startup time.
            try:
                from core.teams.registry import TeamRegistry
                team_record = TeamRegistry.route_goal(goal)
            except Exception:
                team_record = None

        planner_output = self.planner.run(goal)
        research_output = self._maybe_research(goal, planner_output)
        coding_output = self.coder.run(
            {
                "goal": goal,
                "plan": planner_output,
                "research": research_output,
            }
        )

        # Review / iterate.
        aggregated: List[Dict[str, Any]] = []
        critic_output: Dict[str, Any] = {"score": 0, "verdict": "fail", "issues": []}
        for pass_idx in range(max(1, self.settings.consensus_passes)):
            critic_output = self.critic.run(
                {
                    "goal": goal,
                    "planner": planner_output,
                    "research": research_output,
                    "coding": coding_output,
                    "pass": pass_idx,
                }
            )
            aggregated.append(
                {
                    "result": str(
                        {
                            "planner": planner_output,
                            "research": research_output,
                            "coding": coding_output,
                        }
                    ),
                    "review": critic_output,
                }
            )

            score = int(critic_output.get("score", 0) or 0)
            if score >= int(self.settings.review_target_score):
                break

            # Use the critic's feedback to nudge the next pass.
            research_output = self._maybe_research(
                goal,
                {
                    "plan": planner_output,
                    "issues": critic_output.get("issues", []),
                },
                force=True,
            )
            coding_output = self.coder.run(
                {
                    "goal": goal,
                    "plan": planner_output,
                    "research": research_output,
                    "critic_issues": critic_output.get("issues", []),
                }
            )

        consensus_output = self.consensus.evaluate(aggregated)

        # Status decision.
        verdict = (critic_output or {}).get("verdict", "fail")
        confidence = float(consensus_output.get("confidence", 0.0) or 0.0)
        status = "complete" if (verdict == "pass" or confidence >= 0.5) else "needs_revision"

        result = {
            "planner": planner_output,
            "research": research_output,
            "coding": coding_output,
            "critic": critic_output,
            "consensus": consensus_output,
            "status": status,
            "team": team_record,
            "passes": pass_idx + 1,
        }

        task.mark_complete(result)
        self.task_history.append(task)

        # Persist a memory record so the swarm can see what happened.
        try:
            self.memory.add(
                {
                    "type": "executive_run",
                    "goal": goal,
                    "status": status,
                    "score": critic_output.get("score"),
                    "timestamp": time.time(),
                }
            )
        except Exception:
            # A memory-write failure must NEVER take down the run.
            pass

        return result

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #

    def _make_task(self, goal: str) -> Task:
        return Task(
            id=str(uuid.uuid4()),
            goal=goal,
            task_type="goal",
            priority=1,
        )

    def _maybe_research(
        self,
        goal: str,
        plan: Dict[str, Any],
        force: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """Whether research is needed is a primitive heuristic here.

        A real expert-routing model would be the boundary to plug a policy
        LLM into; for now we use keyword detection.
        """
        text = " ".join(
            [
                str(goal).lower(),
                str(plan.get("plan") or "").lower(),
                " ".join(str(i) for i in plan.get("issues", []) or []).lower(),
            ]
        )
        if not force and not any(
            kw in text
            for kw in ("research", "find", "search", "compare", "investigate", "why", "how")
        ):
            return None
        try:
            return self.researcher.run(goal)
        except Exception as exc:  # noqa: BLE001
            return {"agent": "researcher", "error": str(exc)}

    def _empty_result(self, *, reason: str) -> Dict[str, Any]:
        return {
            "planner": {"status": "skipped", "reason": reason},
            "research": None,
            "coding": None,
            "critic": {"score": 0, "verdict": "fail", "issues": [reason]},
            "consensus": {"status": "empty", "result": None, "confidence": 0.0},
            "status": "empty",
            "team": None,
            "passes": 0,
        }


# Backwards compat: prior callers did ``from core.executive_ai import ExecutiveAI``.
ExecutiveAI = MultiAgentExecutive
