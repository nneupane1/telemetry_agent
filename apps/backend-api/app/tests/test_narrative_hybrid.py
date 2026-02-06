"""
NarrativeComposer hybrid selection tests.
"""

from __future__ import annotations

from app.workflows.narrative import NarrativeComposer


class _StaticChain:
    def __init__(self, response: str) -> None:
        self._response = response

    def invoke(self, payload):  # pragma: no cover - tiny shim
        _ = payload
        return self._response


def test_hybrid_returns_deterministic_when_llm_disabled():
    composer = NarrativeComposer()
    composer._llm_enabled = False
    composer._llm_chain = None

    result = composer.compose_hybrid_chat_reply(
        user_message="what is the status?",
        context={"vin": "VIN123", "risk_level": "HIGH"},
        deterministic_reply="VIN VIN123 is currently assessed as HIGH.",
    )

    assert result == "VIN VIN123 is currently assessed as HIGH."


def test_hybrid_prefers_higher_scoring_llm_candidate():
    composer = NarrativeComposer()
    composer._llm_enabled = True
    composer._llm_chain = _StaticChain(
        "VIN VIN123 is currently assessed as HIGH. Evidence sources: MH, MP. "
        "There are 2 recommendation(s) based on the available predictive signals."
    )

    result = composer.compose_hybrid_chat_reply(
        user_message="what is the risk and evidence?",
        context={
            "vin": "VIN123",
            "risk_level": "HIGH",
            "recommendations": [{}, {}],
            "evidence_summary": {"MH": {}, "MP": {}},
        },
        deterministic_reply="VIN VIN123 has active alerts.",
    )

    assert "Evidence sources: MH, MP" in result


def test_hybrid_rejects_speculative_llm_candidate():
    composer = NarrativeComposer()
    composer._llm_enabled = True
    composer._llm_chain = _StaticChain(
        "VIN VIN123 might probably be severe, I think maybe inspect soon."
    )

    deterministic = (
        "VIN VIN123 is currently assessed as HIGH. "
        "Evidence sources: MH."
    )
    result = composer.compose_hybrid_chat_reply(
        user_message="what is the risk?",
        context={
            "vin": "VIN123",
            "risk_level": "HIGH",
            "evidence_summary": {"MH": {}},
        },
        deterministic_reply=deterministic,
    )

    assert result == deterministic
