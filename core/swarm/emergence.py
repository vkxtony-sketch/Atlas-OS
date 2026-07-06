"""
Atlas OS - Emergent Swarm Layer

This module analyzes swarm behavior patterns and derives
structural adjustments for future runs.

Unlike the meta-controller (which tunes parameters),
this layer identifies higher-level behavioral patterns:
- role effectiveness drift
- recurring success patterns
- coordination bottlenecks

It outputs suggestions for system-level reconfiguration.
"""

from typing import Dict, Any
from core.memory.shared_store import SharedMemoryStore
from core.swarm.learning import SwarmLearningEngine


class EmergentSwarmAnalyzer:
    def __init__(self):
        self.memory = SharedMemoryStore()
        self.learning = SwarmLearningEngine()

    def analyze_patterns(self) -> Dict[str, Any]:
        history = self.memory.get_recent(100)

        if not history:
            return {
                "status": "no_data",
                "patterns": {}
            }

        role_counts = {}
        task_frequency = {}

        for entry in history:
            agent = entry.get("agent", "unknown")
            task = entry.get("task", "unknown")

            role_counts[agent] = role_counts.get(agent, 0) + 1
            task_frequency[task] = task_frequency.get(task, 0) + 1

        most_common_tasks = sorted(task_frequency.items(), key=lambda x: x[1], reverse=True)[:5]

        underused_agents = [a for a, c in role_counts.items() if c < max(role_counts.values()) * 0.3]

        return {
            "status": "ok",
            "patterns": {
                "role_activity": role_counts,
                "most_common_tasks": most_common_tasks,
                "underused_agents": underused_agents
            }
        }
