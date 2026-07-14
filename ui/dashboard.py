"""Atlas OS - Streamlit dashboard.

Visual control panel for the Executive. Operates by importing the same
``MultiAgentExecutive`` the CLI and FastAPI server use so behaviour is
identical across entry points.

Sections:
* Manual Goal       — text input + Execute button.
* Autonomous Loop   — start/stop + history view.
* Team Roster       — the eight Atlas spec teams + accept confidence.
* Agent Registry    — the canonical agent role catalog.
* Audit Log         — last N audit rows.
"""
from __future__ import annotations

import json

import streamlit as st

from core.audit.log import recent as audit_recent
from core.agents.registry import list_agents, role_capabilities
from core.autonomous_engine import AutonomousEngine
from core.config import get_settings
from core.executive_ai import MultiAgentExecutive
from core.teams.registry import TeamRegistry


st.set_page_config(page_title="Atlas OS Dashboard", layout="wide")
st.title("🧠 Atlas OS Dashboard")
st.caption(
    "Local-first multi-agent orchestration. Every action is "
    "permission-gated and audit-logged."
)

settings = get_settings()
st.sidebar.subheader("Configuration")
st.sidebar.json({
    "llm_provider": settings.llm_provider,
    "consensus_passes": settings.consensus_passes,
    "review_target_score": settings.review_target_score,
    "autonomous_max_cycles": settings.autonomous_max_cycles,
    "allow_code_execution": settings.allow_code_execution,
    "audit_log_path": settings.audit_log_path,
})

# ------------------------------------------------------------------ state
if "_executive" not in st.session_state:
    st.session_state._executive = MultiAgentExecutive()
if "_autonomous" not in st.session_state:
    st.session_state._autonomous = AutonomousEngine()


executive = st.session_state._executive
autonomous = st.session_state._autonomous


# ------------------------------------------------------------------ manual
st.header("Run a goal")
goal = st.text_input("Goal", key="goal_input",
                    placeholder="e.g. design a recipe website")

col1, col2 = st.columns([1, 1])
with col1:
    if st.button("Execute", type="primary") and goal.strip():
        with st.spinner("Atlas OS planning / researching / coding / reviewing…"):
            result = executive.run_goal(goal.strip())
        st.session_state._last_result = result

with col2:
    if st.button("Clear last result"):
        st.session_state.pop("_last_result", None)


if "_last_result" in st.session_state:
    r = st.session_state._last_result
    st.subheader("Result")
    st.metric("Status", r.get("status", "unknown"))
    c1, c2, c3 = st.columns(3)
    c1.metric("Review score", (r.get("critic") or {}).get("score", 0))
    c2.metric("Passes", r.get("passes", 0))
    c3.metric("Confidence",
              round(float((r.get("consensus") or {}).get("confidence", 0) or 0), 2))

    tab_planner, tab_research, tab_code, tab_critic, tab_consensus = st.tabs(
        ["Planner", "Research", "Coding", "Critic", "Consensus"]
    )
    with tab_planner:
        st.json(r.get("planner"))
    with tab_research:
        st.json(r.get("research"))
    with tab_code:
        st.json(r.get("coding"))
    with tab_critic:
        st.json(r.get("critic"))
    with tab_consensus:
        st.json(r.get("consensus"))


# ------------------------------------------------------------------ auto
st.header("Autonomous engine")
a1, a2 = st.columns(2)
with a1:
    if st.button("Start one cycle"):
        autonomous.run_once()
        st.success("Autonomous cycle executed.")
with a2:
    if st.button("Stop"):
        autonomous.stop()
        st.warning("Autonomous engine stopped.")

st.subheader("History")
history = autonomous.get_history() or []
st.write(f"{len(history)} cycles recorded")


# ------------------------------------------------------------------ teams
st.header("Teams (8)")
teams = TeamRegistry.all()
if not teams:
    st.info("No teams registered.")
else:
    rows = []
    for t in teams:
        rows.append({
            "name": t.name,
            "members": ", ".join(t.members),
            "description": t.description,
        })
    st.table(rows)


# ------------------------------------------------------------------ agents
st.header("Agent registry")
st.code(" ".join(list_agents()), language="text")
cap = role_capabilities()
st.json(cap)


# ------------------------------------------------------------------ audit
st.header("Audit log (last 25)")
rows = audit_recent(25)
if rows:
    st.dataframe(rows, use_container_width=True)
else:
    st.info("No audit rows yet.")

st.sidebar.subheader("Memory")
mem = executive.memory.get_recent(10)
st.sidebar.write(mem if mem else "(empty)")
