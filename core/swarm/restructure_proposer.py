"""
Atlas OS - Autonomous Restructuring Proposal Engine

This module represents the highest-level intelligence layer:
It does NOT modify code or architecture directly.

Instead, it generates restructuring proposals based on:
- emergent swarm patterns
- learning signals
- meta-controller policy drift

These proposals are meant for human or external system review.
"""

from typing import Dict, Any, List

from core.swarm.emergence import EmergentSwarmAnalyzer
from core.swarm.learning import SwarmLearningEngine
from core.swarm.meta_controller import SwarmMetaController


class RestructureProposer:
    def __init__(self):
        self.emergence = EmergentSwarmAnalyzer()
        self.learning = SwarmLearningEngine()
        self.meta = SwarmMetaController()

    def propose(self) -> Dict[str, Any]:
        patterns = self.emergence.analyze_patterns()
        learning_signal = self.learning.analyze()
        policy = self.meta.get_policy()

        suggestions: List[str] = []

        if patterns.get("status") == "ok":
            p = patterns.get("patterns", {})

            if len(p.get("underused_agents", [])) > 0:
                suggestions.append("Consider merging or rebalancing underused agent roles")

            if len(p.get("most_common_tasks", [])) > 3:
                suggestions.append("Introduce specialized agents for repeated high-frequency tasks")

        rec = learning_signal.get("recommendations", {})
        avg = rec.get("average_score", 50)

        if avg < 45:
            suggestions.append("System performance is low: increase exploration and diversify agent strategies")

        if avg > 80:
            suggestions.append("System performance is high: consider optimizing for efficiency and reducing redundancy")

        if policy.get("strategy") == "explore":
            suggestions.append("System is in exploration mode: stabilize successful patterns before further expansion")

        return {
            "status": "ok",
            "policy_snapshot": policy,
            "learning_snapshot": rec,
            "patterns_snapshot": patterns,
            "restructure_suggestions": suggestions
        }
