"""
Atlas OS - Self-Improving Swarm Learning Engine

This module analyzes shared swarm memory and produces
adaptive improvements for future execution cycles.

It does NOT modify code automatically — it generates
learning signals for the orchestrator.
"""

from typing import Dict, Any
from core.memory.shared_store import SharedMemoryStore


class SwarmLearningEngine:
    def __init__(self):
        self.memory = SharedMemoryStore()

    def analyze(self) -> Dict[str, Any]:
        history = self.memory.get_recent(50)

        total = len(history)
        if total == 0:
            return {
                "status": "no_data",
                "recommendations": {}
            }

        scores = []

        for item in history:
            eval_data = str(item.get("evaluation", ""))

            if "bad" in eval_data.lower() or "low" in eval_data.lower():
                scores.append(30)
            elif "average" in eval_data.lower():
                scores.append(60)
            elif "good" in eval_data.lower() or "high" in eval_data.lower():
                scores.append(85)
            else:
                scores.append(50)

        avg_score = sum(scores) / len(scores)

        recommendations = {
            "average_score": avg_score,
            "cycle_adjustment": "increase" if avg_score > 70 else "decrease",
            "strategy": "explore" if avg_score < 50 else "exploit",
            "memory_size": total
        }

        return {
            "status": "ok",
            "recommendations": recommendations
        }
