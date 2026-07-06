"""
Atlas OS - UI Dashboard (Streamlit)

This is the visual control center for Atlas OS.
It allows users to:
- Run goals interactively
- View execution results
- Inspect memory
- Control autonomous engine
"""

import streamlit as st
from core.executive_ai import ExecutiveAI
from core.autonomous_engine import AutonomousEngine

st.set_page_config(page_title="Atlas OS Dashboard", layout="wide")

st.title("🧠 Atlas OS Dashboard")

# Initialize systems
if "executive" not in st.session_state:
    st.session_state.executive = ExecutiveAI()

if "autonomous" not in st.session_state:
    st.session_state.autonomous = AutonomousEngine()

executive = st.session_state.executive
autonomous = st.session_state.autonomous

# Sidebar controls
st.sidebar.header("Controls")
mode = st.sidebar.selectbox("Mode", ["Manual", "Autonomous"])

# Manual mode
if mode == "Manual":
    st.subheader("Run a Goal")
    goal = st.text_input("Enter goal")

    if st.button("Execute") and goal:
        result = executive.run_goal(goal)
        st.session_state.last_result = result

    if "last_result" in st.session_state:
        st.subheader("Result")
        st.json(st.session_state.last_result)

# Autonomous mode
if mode == "Autonomous":
    st.subheader("Autonomous Engine")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Start Autonomous Loop"):
            autonomous.run_once()
            st.success("Autonomous cycle executed")

    with col2:
        if st.button("Stop"):
            autonomous.stop()
            st.warning("Autonomous engine stopped")

    st.subheader("History")
    st.write(autonomous.get_history())

# Memory viewer
st.sidebar.subheader("Memory")
st.json(executive.memory.store)
