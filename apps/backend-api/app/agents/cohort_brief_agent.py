"""
Cohort Brief Agent.

This agent converts aggregated cohort metrics and detected anomalies
into a concise, executive-level fleet interpretation.

Used by:
- GenAI interpreter service
- Cohort API endpoints
- Executive dashboards and briefings
"""

from __future__ import annotations

from typing import Any, Dict, List

from app.models.cohort import (
    CohortAnomaly,
    CohortInterpretation,
    CohortMetric,
)
from app.utils.logger import (
    get_logger,
    log_event,
    set_agent,
)

logger = get_logger(__name__)


class CohortBriefAgent:
    """
    Agent responsible for cohort-level narrative interpretation.
    """

    def __init__(self, *, model_version: str) -> None:
        self._model_version = model_version

    # -----------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------

    def explain(
        self,
        *,
        cohort_id: str,
        metrics: List[Dict[str, Any]],
        anomalies: List[Dict[str, Any]],
        cohort_description: str | None = None,
    ) -> CohortInterpretation:
        """
        Produce a cohort-level interpretation from aggregated inputs.
        """

        set_agent("cohort_brief")

        log_event(
            logger,
            "Starting cohort briefing",
            extra={
                "cohort_id": cohort_id,
                "metric_count": len(metrics),
                "anomaly_count": len(anomalies),
            },
        )

        metric_models = self._build_metrics(metrics)
        anomaly_models = self._build_anomalies(anomalies)

        summary = self._generate_summary(metric_models, anomaly_models)

        interpretation = CohortInterpretation(
            cohort_id=cohort_id,
            cohort_description=cohort_description,
            summary=summary,
            metrics=metric_models,
            anomalies=anomaly_models,
            risk_distribution=self._risk_distribution(metrics),
            model_version=self._model_version,
        )

        log_event(
            logger,
            "Cohort briefing completed",
            extra={
                "cohort_id": cohort_id,
                "anomalies_reported": len(anomaly_models),
            },
        )

        return interpretation

    # -----------------------------------------------------------------
    # Internal helpers
    # -----------------------------------------------------------------

    def _build_metrics(
        self,
        raw_metrics: List[Dict[str, Any]],
    ) -> List[CohortMetric]:
        return [
            CohortMetric(
                name=m["metric_name"],
                value=float(m["metric_value"]),
                unit=m.get("unit"),
                description=m.get("description", ""),
            )
            for m in raw_metrics
        ]

    def _build_anomalies(
        self,
        raw_anomalies: List[Dict[str, Any]],
    ) -> List[CohortAnomaly]:
        return [
            CohortAnomaly(
                title=a["title"],
                description=a["description"],
                affected_vin_count=int(a["affected_vin_count"]),
                severity=a["severity"],
                related_signals=a.get("related_signals", []),
            )
            for a in raw_anomalies
        ]

    def _generate_summary(
        self,
        metrics: List[CohortMetric],
        anomalies: List[CohortAnomaly],
    ) -> str:
        """
        Deterministic executive summary (LLM-safe baseline).
        """

        high_severity = [
            a for a in anomalies if a.severity.upper() == "HIGH"
        ]

        if high_severity:
            return (
                "Fleet health remains broadly stable, however multiple "
                "high-severity anomalies require immediate attention."
            )

        if anomalies:
            return (
                "Several emerging risk patterns have been identified and "
                "should be monitored closely."
            )

        return "No significant fleet-level anomalies detected at this time."

    def _risk_distribution(
        self,
        metrics: List[Dict[str, Any]],
    ) -> Dict[str, int] | None:
        """
        Extract risk distribution if present in metrics.
        """

        distribution = {}
        for m in metrics:
            if m.get("metric_name", "").startswith("risk_"):
                distribution[m["metric_name"].replace("risk_", "").upper()] = int(
                    m["metric_value"]
                )

        return distribution or None
