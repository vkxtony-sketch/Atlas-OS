"""
Atlas OS - CLI Runtime Launcher

This is the entry point for running Atlas OS as a local multi-agent system.

Usage:
    python main.py "your goal here"

Example:
    python main.py "design a landing page"
"""

import sys
from core.executive_ai import ExecutiveAI


def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py \"your goal\"")
        return

    goal = " ".join(sys.argv[1:])

    print("\n🚀 Atlas OS Starting...\n")
    print(f"🎯 Goal: {goal}\n")

    executive = ExecutiveAI()
    result = executive.run_goal(goal)

    print("\n===== ATLAS OS RESULT =====\n")
    print("📌 Planner Output:", result["planner"])
    print("\n📚 Research Output:", result["research"])
    print("\n💻 Coding Output:", result["coding"])
    print("\n🧠 Critic Output:", result["critic"])
    print("\n🧩 Consensus:", result["consensus"])
    print("\n✅ Status:", result["status"])

    print("\n===========================\n")


if __name__ == "__main__":
    main()
