"""
Atlas OS - Swarm Meta Controller (Self-Modifying Behavior Layer)

This module enables the system to adapt its OWN runtime behavior
WITHOUT modifying source code.

Instead, it dynamically adjusts:
- swarm cycle limits
- agent weighting strategies
- exploration vs exploitation balance
- tool usage preference signals

This is the "self-modifying behavior layer" of Atlas OS.
"""

from typing import Dict, Any

from core.swarm.learning import SwarmLearningEngine


class SwarmMetaController:
    def __init__(self):
        self.learning = SwarmLearningEngine()

        self.policy = {
            "max_cycles": 5,
            "agent_weight_planner": 1.0,
            "agent_weight_researcher": 1.0,
            "agent_weight_coder": 1.0,
            "agent_weight_critic": 1.0,
            "strategy": "balanced",
            "tool_aggressiveness": 1.0
        }

    def update_policy(self) -> Dict[str, Any]:
        signal = self.learning.analyze()
        rec = signal.get("recommendations", {})

        avg = rec.get("average_score", 50)
        strategy = rec.get("strategy", "exploit")
        cycle_adj = rec.get("cycle_adjustment", "decrease")

        if cycle_adj == "increase":
            self.policy["max_cycles"] = min(10, self.policy["max_cycles"] + 1)
        else:
            self.policy["max_cycles"] = max(2, self.policy["max_cycles"] - 1)

        self.policy["strategy"] = strategy

        if avg < 50:
            self.policy["agent_weight_researcher"] += 0.1
            self.policy["agent_weight_planner"] += 0.1
            self.policy["agent_weight_coder"] -= 0.05
        else:
            self.policy["agent_weight_coder"] += 0.1
            self.policy["agent_weight_critic"] += 0.05

        for k in self.policy:
            if isinstance(self.policy[k], float):
                self.policy[k] = max(0.1, min(2.0, self.policy[k]))

        return {
            "status": "updated",
            "policy": self.policy,
            "signal": signal
        }

    def get_policy(self) -> Dict[str, Any]:
        return self.policy
