import pytest

from core.consensus_engine import ConsensusEngine


def test_consensus_majority_and_confidence():
    engine = ConsensusEngine()

    result = engine.evaluate(
        [
            {"result": "alpha"},
            {"result": "beta"},
            {"result": "alpha"},
        ]
    )

    assert result["result"] == "alpha"
    assert result["consensus_result"] == "alpha"
    assert result["confidence"] == pytest.approx(2 / 3)
    assert result["total_votes"] == 3
    assert result["status"] == "consensus"


def test_consensus_empty_case():
    engine = ConsensusEngine()

    result = engine.evaluate([])

    assert result == {
        "status": "empty",
        "result": None,
        "consensus_result": None,
        "confidence": 0.0,
        "total_votes": 0,
    }
