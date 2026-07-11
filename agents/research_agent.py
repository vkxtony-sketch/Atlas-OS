"""
Atlas OS - Research Agent

The Research Agent is responsible for:
- Gathering deterministic search results for a task goal
- Providing lightweight research context to downstream agents
"""

from typing import Any, Dict

from core.agent import Agent
from core.task import Task
from core.tools.web_tool import WebTool


class ResearchAgent(Agent):
    def __init__(self):
        super().__init__(name="research_agent", role="research")
        self.web_tool = WebTool()

    def run(self, task: Task) -> Dict[str, Any]:
        research = self.web_tool.search(task.goal)

        return {
            "goal": task.goal,
            "research": research,
            "status": "researched",
        }
