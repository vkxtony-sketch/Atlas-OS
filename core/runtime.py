"""
Atlas OS - Final Integrated Runtime

This module wires together ALL components:
- LLM layer (real or mock)
- Tool router (web + python)
- Agent orchestration (planner/coder/critic simulation)
- Autonomous compatibility layer

This is the "glue" that turns Atlas OS from architecture
into a working cognitive system.
"""

from core.llm import LLM
from core.tools.router import ToolRouter


class AtlasRuntime:
    def __init__(self):
        self.llm = LLM()
        self.tools = ToolRouter()

    def run_goal(self, goal: str) -> dict:
        """
        Full integrated execution pipeline:
        1. Route tool usage
        2. Use LLM reasoning
        3. Optionally execute tools
        4. Produce structured result
        """

        tool_result = self.tools.route(goal)

        reasoning_prompt = f"""
You are Atlas OS Executive AI.
Goal: {goal}

Tool Result:
{tool_result}

You must:
- interpret tool output
- produce final structured solution
- explain reasoning briefly
"""

        llm_output = self.llm.complete(reasoning_prompt)

        return {
            "goal": goal,
            "tool": tool_result,
            "output": llm_output
        }


# Backwards compatibility alias
ExecutiveAI = AtlasRuntime
