"""
Atlas OS - Python Execution Tool (Sandboxed Stub)

Allows agents to execute Python code in a controlled environment.
In production, this should be replaced with a secure sandbox (Docker / subprocess isolation).

For now:
- Executes code in a restricted namespace
- Returns stdout-like result dictionary
"""

import traceback
from typing import Any, Dict


class PythonTool:
    def __init__(self):
        self.globals = {}

    def run(self, code: str) -> Dict[str, Any]:
        """
        Execute Python code and return result or error.
        WARNING: This is NOT secure for production use.
        """

        local_vars = {}

        try:
            exec(code, self.globals, local_vars)
            return {
                "status": "success",
                "output": local_vars
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "trace": traceback.format_exc()
            }
