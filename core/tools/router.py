"""
Atlas OS - Tool Router

This module decides which tool an agent should use:
- LLM only
- Web search
- Python execution

In a real system, this would be driven by a policy model.
Here it is a lightweight heuristic router.
"""

from typing import Any, Dict

from core.tools.web_tool import WebTool
from core.tools.python_tool import PythonTool


class ToolRouter:
    def __init__(self):
        self.web = WebTool()
        self.python = PythonTool()

    def route(self, task: str) -> Dict[str, Any]:
        task_lower = task.lower()

        if "search" in task_lower or "find" in task_lower or "look up" in task_lower:
            return {
                "tool": "web",
                "result": self.web.search(task)
            }

        if "calculate" in task_lower or "run code" in task_lower or "python" in task_lower:
            return {
                "tool": "python",
                "result": self.python.run(task)
            }

        return {
            "tool": "llm",
            "result": None
        }

