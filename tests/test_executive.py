"""Smoke tests for the ExecutiveAI contract.

These tests do NOT depend on the package being installed. They sit
alongside ``core/`` and are run with ``pytest tests/``.
"""
from __future__ import annotations

import os
import sys

import pytest

# Make project root importable without an install step.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.executive_ai import MultiAgentExecutive  # noqa: E402
from core.teams.registry import TeamRegistry  # noqa: E402

import core.teams  # noqa: F401,E402  - registers the 8 teams on import


def test_executive_returns_contract_keys():
    execu = MultiAgentExecutive()
    result = execu.run_goal("design a recipe website")
    assert "planner" in result
    assert "research" in result  # allowed to be None
    assert "coding" in result
    assert "critic" in result
    assert "consensus" in result
    assert "status" in result
    assert result["status"] in {"complete", "needs_revision", "empty"}


def test_executive_status_advanced_for_research_goal():
    execu = MultiAgentExecutive()
    result = execu.run_goal("research the best Python web framework")
    assert result["status"] in {"complete", "needs_revision"}
    # Critic must produce a numeric score.
    assert isinstance(result["critic"].get("score"), int)


def test_executive_blank_goal_returns_empty():
    execu = MultiAgentExecutive()
    result = execu.run_goal("   ")
    assert result["status"] == "empty"
    assert result["critic"]["score"] == 0


def test_executive_records_history():
    execu = MultiAgentExecutive()
    execu.run_goal("first goal")
    execu.run_goal("second goal")
    assert len(execu.task_history) >= 2
    assert execu.task_history[-1].goal == "second goal"


def test_team_registry_has_eight_teams():
    assert len(TeamRegistry.all()) == 8
    names = {t.name for t in TeamRegistry.all()}
    expected = {"architecture", "backend", "frontend", "security",
                "performance", "documentation", "testing", "research"}
    assert expected.issubset(names)


def test_team_routing_prefers_specific_team():
    decision = TeamRegistry.route_goal("design a database schema for the API")
    # Schema/API/database keywords should pick the backend team first.
    assert decision["primary"] in {"backend", "architecture"}
