"""
Atlas OS - Consensus Engine

The Consensus Engine aggregates outputs from multiple agents
and produces a single agreed-upon result.
"""

from typing import Any, Dict, List


class ConsensusEngine:
    def __init__(self):
        self.history: List[Dict[str, Any]] = []

    def evaluate(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Basic consensus strategy:
        - Count frequency of identical results
        - Pick most common output
        - Attach confidence score
        """
        if not results:
            return {"status": "empty", "result": None}

        frequency: Dict[str, int] = {}

        for r in results:
            key = str(r.get("result"))
            frequency[key] = frequency.get(key, 0) + 1

        best_result = max(frequency.items(), key=lambda x: x[1])

        consensus = {
            "consensus_result": best_result[0],
            "confidence": best_result[1] / len(results),
            "total_votes": len(results)
        }

        self.history.append(consensus)
        return consensus

    def get_history(self) -> List[Dict[str, Any]]:
        return self.history
