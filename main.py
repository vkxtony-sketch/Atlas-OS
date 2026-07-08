"""
Atlas OS - CLI Runtime Launcher

This is the entry point for running Atlas OS as a local multi-agent system.

Usage:
    python main.py "your goal here"

Example:
    python main.py "design a landing page"
"""

import json
import sys

from core.executive_ai import ExecutiveAI


def main() -> int:
    if len(sys.argv) < 2:
        print('Usage: python main.py "your goal"')
        return 1

    goal = " ".join(sys.argv[1:])

    print("\nAtlas OS Starting...\n")
    print(f"Goal: {goal}\n")

    executive = ExecutiveAI()
    result = executive.run_goal(goal)

    print("===== ATLAS OS RESULT =====\n")
    for key in ("planner", "research", "coding", "critic", "consensus"):
        print(f"{key.upper()}:")
        print(json.dumps(result[key], indent=2, ensure_ascii=False))
        print()

    print(f"STATUS: {result['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
