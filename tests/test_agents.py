from agents import CodingAgent, CriticAgent, PlannerAgent, ResearchAgent
from core.task import Task


def test_planner_agent_run():
    result = PlannerAgent().run(Task(id="1", goal="build a landing page"))
    assert result["status"] == "planned"


def test_research_agent_run():
    result = ResearchAgent().run(Task(id="1", goal="build a landing page"))
    assert result["status"] == "researched"
    assert "research" in result


def test_coding_agent_run():
    result = CodingAgent().run(Task(id="1", goal="build a landing page"))
    assert result["status"] == "generated"


def test_critic_agent_run():
    task = Task(id="1", goal="build a landing page")
    task.metadata.update(
        {
            "planner_output": {"status": "planned"},
            "research_output": {"status": "researched"},
            "coding_output": {"status": "generated"},
        }
    )
    result = CriticAgent().run(task)
    assert result["status"] == "evaluated"
    assert result["verdict"] == "pass"
