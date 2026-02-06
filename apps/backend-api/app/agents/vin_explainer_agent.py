"""
VIN Explainer Agent.

This agent converts normalized VIN-level predictive signals into a
clear, human-readable interpretation using an LLM, grounded by
reference dictionaries and strict output contracts.

Used by:
- GenAI interpreter service
- VIN API endpoints
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List

from app.models.vin import (
    EvidenceItem,
    Recommendation,
    VinInterpretation,
)
from app.utils.logger import (
    get_logger,
    log_event,
    set_agent,
    set_vin,
)

logger = get_logger(__name__)


class VinExplainerAgent:
    """
    Agent responsible for VIN-level narrative interpretation.
    """

    def __init__(self, *, model_version: str) -> None:
        self._model_version = model_version

    # -----------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------

    def explain(
        self,
        *,
        vin: str,
        mh_signals: List[Dict[str, Any]],
        mp_signals: List[Dict[str, Any]],
        fim_signals: List[Dict[str, Any]],
        reference_map: Dict[str, Dict[str, Any]],
    ) -> VinInterpretation:
        """
        Produce a VIN-level interpretation from predictive signals.
        """

        set_agent("vin_explainer")
        set_vin(vin)

        log_event(
            logger,
            "Starting VIN explanation",
            extra={
                "mh_count": len(mh_signals),
                "mp_count": len(mp_signals),
                "fim_count": len(fim_signals),
            },
        )

        evidence = self._build_evidence(
            mh_signals,
            mp_signals,
            fim_signals,
            reference_map,
        )

        summary, risk_level = self._generate_summary(evidence)
        recommendations = self._generate_recommendations(evidence)

        interpretation = VinInterpretation(
            vin=vin,
            summary=summary,
            risk_level=risk_level,
            recommendations=recommendations,
            model_version=self._model_version,
        )

        log_event(
            logger,
            "VIN explanation completed",
            extra={
                "risk_level": risk_level,
                "recommendation_count": len(recommendations),
            },
        )

        return interpretation

    def answer_question(
        self,
        *,
        question: str,
        context: Dict[str, Any],
    ) -> str:
        """
        Provide bounded VIN-focused explainability answers for chat.
        """
        vin = str(context.get("vin", "UNKNOWN")).upper()
        risk_level = context.get("risk_level")
        recommendations = context.get("recommendations")
        evidence_summary = context.get("evidence_summary")

        recommendation_count = (
            len(recommendations) if isinstance(recommendations, list) else None
        )

        if risk_level and recommendation_count is not None:
            evidence_sources = (
                ", ".join(sorted(evidence_summary.keys()))
                if isinstance(evidence_summary, dict)
                else "none"
            )
            return (
                f"VIN {vin} is currently assessed as {risk_level}. "
                f"There are {recommendation_count} recommendation(s) based on "
                "predictive evidence from MH/MP/FIM signals. "
                f"Evidence sources: {evidence_sources}."
            )

        if risk_level:
            return (
                f"VIN {vin} is currently assessed as {risk_level}. "
                "Share recommendations/evidence context for a deeper explanation."
            )

        _ = question  # reserved for future prompt-based routing
        return (
            f"I can explain VIN {vin} risk signals and recommendations. "
            "Provide risk level and evidence context for specific details."
        )

    # -----------------------------------------------------------------
    # Internal helpers
    # -----------------------------------------------------------------

    def _build_evidence(
        self,
        mh: List[Dict[str, Any]],
        mp: List[Dict[str, Any]],
        fim: List[Dict[str, Any]],
        ref: Dict[str, Dict[str, Any]],
    ) -> List[EvidenceItem]:
        """
        Normalize raw mart rows into EvidenceItem objects.
        """

        evidence: List[EvidenceItem] = []

        for source, rows in {
            "MH": mh,
            "MP": mp,
            "FIM": fim,
        }.items():
            for row in rows:
                code = (
                    row.get("signal_code")
                    or row.get("hi_code")
                    or row.get("trigger_code")
                    or row.get("rootcause_code")
                )
                if not code:
                    continue

                ref_entry = ref.get(code, {})
                family = ref_entry.get("family")
                description = ref_entry.get(
                    "description",
                    "No description available",
                )
                if family and family != "UNKNOWN":
                    description = f"{description} ({family})"

                confidence = (
                    row.get("confidence")
                    or row.get("trigger_probability")
                    or row.get("rootcause_probability")
                    or 0.0
                )
                observed_at = (
                    row.get("observed_at")
                    or row.get("trigger_time")
                    or row.get("event_time")
                    or datetime.utcnow()
                )

                evidence.append(
                    EvidenceItem(
                        source_model=source,
                        signal_code=code,
                        signal_description=description,
                        confidence=float(confidence),
                        observed_at=observed_at,
                    )
                )

        return evidence

    def _generate_summary(
        self,
        evidence: List[EvidenceItem],
    ) -> tuple[str, str]:
        """
        Generate a high-level summary and risk classification.
        """

        # Deterministic fallback logic (LLM-safe baseline)
        high_conf = [e for e in evidence if e.confidence >= 0.8]

        if len(high_conf) >= 3:
            risk = "HIGH"
            summary = (
                "Multiple high-confidence predictive signals indicate "
                "a significant elevated risk for this vehicle."
            )
        elif high_conf:
            risk = "ELEVATED"
            summary = (
                "One or more predictive signals suggest an elevated risk "
                "that should be monitored."
            )
        else:
            risk = "LOW"
            summary = (
                "No high-confidence predictive anomalies detected at this time."
            )

        return summary, risk

    def _generate_recommendations(
        self,
        evidence: List[EvidenceItem],
    ) -> List[Recommendation]:
        """
        Generate actionable recommendations based on evidence.
        """

        recommendations: List[Recommendation] = []
        seen_signals = set()

        for ev in evidence:
            if ev.confidence < 0.7:
                continue
            if ev.signal_code in seen_signals:
                continue
            seen_signals.add(ev.signal_code)

            recommendations.append(
                Recommendation(
                    title=f"Investigate {ev.signal_description}",
                    rationale=(
                        f"The signal {ev.signal_code} was detected with "
                        f"{int(ev.confidence * 100)}% confidence."
                    ),
                    urgency="HIGH" if ev.confidence >= 0.85 else "MEDIUM",
                    suggested_action=(
                        "Schedule inspection or diagnostic check "
                        "during the next service window."
                    ),
                    evidence=[ev],
                )
            )

        return recommendations
