"""
GenAIInterpreter orchestration tests.

These tests validate correct sequencing of data loading,
agent execution, and output assembly.
"""

from datetime import datetime
from unittest.mock import MagicMock

from app.models.vin import VinInterpretation
from app.models.cohort import CohortInterpretation
from app.services.genai_interpreter import GenAIInterpreter


def test_interpret_vin_end_to_end(monkeypatch):
    interpreter = GenAIInterpreter(model_version="test")

    # Mock mart loader
    fake_now = datetime.utcnow()

    interpreter._mart_loader.load_mh_snapshot = MagicMock(
        return_value=[
            {
                "hi_code": "HI-4302",
                "confidence": 0.92,
                "observed_at": fake_now,
            }
        ]
    )
    interpreter._mart_loader.load_mp_triggers = MagicMock(return_value=[])
    interpreter._mart_loader.load_fim_root_causes = MagicMock(return_value=[])

    reference_map = {
        "HI-4302": {"description": "Fuel pressure instability detected"}
    }

    result = interpreter.interpret_vin(
        vin="VIN123",
        reference_map=reference_map,
        request_id="test-request",
    )

    assert isinstance(result, VinInterpretation)
    assert result.vin == "VIN123"
    assert result.recommendations
    assert result.evidence_summary
    assert result.model_version == "test"


def test_interpret_cohort_end_to_end(monkeypatch):
    interpreter = GenAIInterpreter(model_version="test")

    interpreter._mart_loader.load_cohort_metrics = MagicMock(
        return_value=[
            {
                "metric_name": "risk_high",
                "metric_value": 12,
                "description": "High-risk vehicles",
            }
        ]
    )

    interpreter._mart_loader.load_cohort_anomalies = MagicMock(
        return_value=[
            {
                "title": "Fuel system anomaly spike",
                "description": "Unusual increase in fuel system alerts",
                "affected_vin_count": 8,
                "severity": "HIGH",
                "related_signals": ["HI-4302"],
            }
        ]
    )

    result = interpreter.interpret_cohort(
        cohort_id="TEST_COHORT",
        request_id="test-request",
    )

    assert isinstance(result, CohortInterpretation)
    assert result.cohort_id == "TEST_COHORT"
    assert result.anomalies
    assert result.model_version == "test"
