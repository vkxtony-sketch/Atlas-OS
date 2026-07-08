from pathlib import Path

from core.executive_ai import ExecutiveAI


def test_executive_run_goal_returns_sections_and_tracks_history():
    memory_file = Path("atlas_memory.json")
    if memory_file.exists():
        memory_file.unlink()

    executive = ExecutiveAI()
    initial_history = len(executive.task_history)

    result = executive.run_goal("build a landing page")

    assert set(result) == {"planner", "research", "coding", "critic", "consensus", "status"}
    assert result["status"] == "complete"
    assert len(executive.task_history) == initial_history + 1
    assert executive.task_history[-1].goal == "build a landing page"
    assert executive.memory.data["history"][-1]["goal"] == "build a landing page"

    if memory_file.exists():
        memory_file.unlink()
