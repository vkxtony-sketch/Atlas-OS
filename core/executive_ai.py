"""
Atlas OS - Executive AI Core

The Executive AI is the top-level orchestrator responsible for:
- Decomposing goals into tasks
- Assigning tasks to agent teams
- Evaluating outputs
- Iterating until convergence
"""

from uuid import uuid4
from typing import Any, Dict, List

from core.consensus_engine import ConsensusEngine
from core.memory import MemoryStore
from core.task import Task


class ExecutiveAI:
    def __init__(self):
        from agents import CodingAgent, CriticAgent, PlannerAgent, ResearchAgent

        self.planner = PlannerAgent()
        self.researcher = ResearchAgent()
        self.coder = CodingAgent()
        self.critic = CriticAgent()
        self.consensus = ConsensusEngine()
        self.memory = MemoryStore()
        self.task_history: List[Task] = []

    def run_goal(self, goal: str) -> Dict[str, Any]:
        task = Task(id=uuid4().hex, goal=goal)
        task.mark_running()

        planner_output = self.planner.run(task)
        research_output = self.researcher.run(task)
        coding_output = self.coder.run(task)

        task.metadata.update(
            {
                "planner_output": planner_output,
                "research_output": research_output,
                "coding_output": coding_output,
            }
        )
        critic_output = self.critic.run(task)

        consensus_input = [
            {"result": planner_output.get("status", "planned")},
            {"result": research_output.get("status", "researched")},
            {"result": coding_output.get("status", "generated")},
            {"result": critic_output.get("verdict", "review")},
        ]
        consensus_output = self.consensus.evaluate(consensus_input)

        result = {
            "planner": planner_output,
            "research": research_output,
            "coding": coding_output,
            "critic": critic_output,
            "consensus": consensus_output,
            "status": "complete",
        }

        task.metadata["consensus_output"] = consensus_output
        task.mark_complete(result)
        self.task_history.append(task)
        self.memory.add(
            {
                "task_id": task.id,
                "goal": goal,
                "status": task.status,
                "result": result,
            }
        )

        return result
