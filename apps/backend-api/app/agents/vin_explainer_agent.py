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

from typing import Any, Dict, List

from app.models.vin import (
    EvidenceItem,
    Recommendation,
    VinInterpretation,
)
from app.utils.config import load_config
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
        self._config = load_config()
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
                code = row.get("signal_code") or row.get("hi_code")
                ref_entry = ref.get(code, {})

                evidence.append(
                    EvidenceItem(
                        source_model=source,
                        signal_code=code,
                        signal_description=ref_entry.get(
                            "description",
                            "No description available",
                        ),
                        confidence=float(row.get("confidence", 0.0)),
                        observed_at=row["observed_at"],
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

        for ev in evidence:
            if ev.confidence < 0.7:
                continue

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
