"""Atlas OS - Performance Team."""
from __future__ import annotations

from core.teams.base import Team


class PerformanceTeam(Team):
    name = "performance"
    description = "Memory, CPU, GPU, algorithm complexity."
    responsibilities = ["Reduce hot-path cost", "Watch cache locality", "Profile"]
    review_focus = [
        "performance", "speed", "fast", "slow", "optimize", "optimise",
        "benchmark", "memory", "cpu", "gpu", "latency", "throughput",
        "complexity", "big-o", "big_o",
    ]
    members = ["performance_reviewer"]
