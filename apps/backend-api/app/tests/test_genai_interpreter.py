"""
GenAIInterpreter orchestration tests.

These tests validate correct sequencing of data loading,
agent execution, and output assembly.
"""

from datetime import datetime
from unittest.mock import MagicMock

import pytest

from app.models.vin import VinInterpretation
from app.models.cohort import CohortInterpretation
from app.services.genai_interpreter import GenAIInterpreter
from app.utils.config import load_config


@pytest.fixture(autouse=True)
def _local_runtime_flags(monkeypatch):
    monkeypatch.setenv("FEATURE_LANGGRAPH", "true")
    monkeypatch.setenv("FEATURE_ALLOW_DETERMINISTIC_FALLBACK", "true")
    load_config.cache_clear()
    yield
    load_config.cache_clear()


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


def test_generate_chat_reply_vin_uses_hybrid_selector(monkeypatch):
    interpreter = GenAIInterpreter(model_version="test")

    context = {
        "vin": "VIN123",
        "risk_level": "HIGH",
        "recommendations": [{"title": "Inspect HI-4302"}],
        "evidence_summary": {"MH": {"count": 1}},
    }

    interpreter._vin_agent.answer_question = MagicMock(return_value="deterministic-vin-reply")
    interpreter._graph_runner.compose_chat_reply = MagicMock(return_value="hybrid-vin-reply")

    reply = interpreter.generate_chat_reply(
        user_message="What should we do next?",
        context=context,
        request_id="test-request",
    )

    assert reply == "hybrid-vin-reply"
    interpreter._graph_runner.compose_chat_reply.assert_called_once()
    kwargs = interpreter._graph_runner.compose_chat_reply.call_args.kwargs
    assert kwargs["deterministic_reply"] == "deterministic-vin-reply"


def test_generate_chat_reply_cohort_uses_hybrid_selector(monkeypatch):
    interpreter = GenAIInterpreter(model_version="test")

    context = {
        "cohort_id": "TEST_COHORT",
        "anomaly_count": 4,
        "risk_distribution": {"HIGH": 2, "ELEVATED": 2},
    }

    interpreter._cohort_agent.answer_question = MagicMock(
        return_value="deterministic-cohort-reply"
    )
    interpreter._graph_runner.compose_chat_reply = MagicMock(
        return_value="hybrid-cohort-reply"
    )

    reply = interpreter.generate_chat_reply(
        user_message="How severe is this cohort?",
        context=context,
        request_id="test-request",
    )

    assert reply == "hybrid-cohort-reply"
    interpreter._graph_runner.compose_chat_reply.assert_called_once()
    kwargs = interpreter._graph_runner.compose_chat_reply.call_args.kwargs
    assert kwargs["deterministic_reply"] == "deterministic-cohort-reply"
