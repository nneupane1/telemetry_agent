"""
VIN interpretation unit tests.

These tests validate deterministic VIN-level interpretation behavior
using controlled, synthetic inputs.
"""

from datetime import datetime

import pytest

from app.agents.vin_explainer_agent import VinExplainerAgent
from app.models.vin import EvidenceItem, VinInterpretation


@pytest.fixture
def reference_map():
    return {
        "HI-4302": {
            "description": "Fuel pressure instability detected",
        }
    }


@pytest.fixture
def sample_signals():
    now = datetime.utcnow()
    return {
        "mh": [
            {
                "hi_code": "HI-4302",
                "confidence": 0.9,
                "observed_at": now,
            }
        ],
        "mp": [],
        "fim": [],
    }


def test_vin_interpretation_high_risk(reference_map, sample_signals):
    agent = VinExplainerAgent(model_version="test")

    result = agent.explain(
        vin="wvwzzz1kz6w000001",
        mh_signals=sample_signals["mh"],
        mp_signals=sample_signals["mp"],
        fim_signals=sample_signals["fim"],
        reference_map=reference_map,
    )

    assert isinstance(result, VinInterpretation)
    assert result.vin == "WVWZZZ1KZ6W000001"
    assert result.risk_level in {"ELEVATED", "HIGH"}
    assert len(result.recommendations) == 1

    rec = result.recommendations[0]
    assert rec.urgency in {"MEDIUM", "HIGH"}
    assert rec.evidence
    assert isinstance(rec.evidence[0], EvidenceItem)


def test_vin_interpretation_low_risk(reference_map):
    agent = VinExplainerAgent(model_version="test")

    result = agent.explain(
        vin="TESTVIN000",
        mh_signals=[],
        mp_signals=[],
        fim_signals=[],
        reference_map=reference_map,
    )

    assert result.risk_level == "LOW"
    assert result.recommendations == []
