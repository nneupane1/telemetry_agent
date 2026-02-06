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

    def answer_question(
        self,
        *,
        question: str,
        context: Dict[str, Any],
    ) -> str:
        """
        Provide bounded cohort explainability answers for chat.
        """
        cohort_id = str(context.get("cohort_id", "UNKNOWN"))
        anomaly_count = context.get("anomaly_count")
        risk_distribution = context.get("risk_distribution")

        if isinstance(risk_distribution, dict):
            parts = [
                f"{level.upper()}={count}"
                for level, count in risk_distribution.items()
            ]
            return (
                f"Cohort {cohort_id} risk distribution: "
                + ", ".join(parts)
                + "."
            )

        if anomaly_count is not None:
            return (
                f"Cohort {cohort_id} currently has {anomaly_count} "
                "reported anomaly pattern(s)."
            )

        _ = question  # reserved for future prompt-based routing
        return (
            f"I can explain cohort {cohort_id} anomalies, risk distribution, "
            "and summary trends. Provide cohort metrics/anomaly context."
        )

    # -----------------------------------------------------------------
    # Internal helpers
    # -----------------------------------------------------------------

    def _build_metrics(
        self,
        raw_metrics: List[Dict[str, Any]],
    ) -> List[CohortMetric]:
        metrics: List[CohortMetric] = []
        for metric in raw_metrics:
            name = metric.get("metric_name") or metric.get("name")
            if not name:
                continue
            value = metric.get("metric_value", metric.get("value", 0.0))
            metrics.append(
                CohortMetric(
                    name=str(name),
                    value=float(value),
                    unit=metric.get("unit"),
                    description=metric.get("description", ""),
                )
            )
        return metrics

    def _build_anomalies(
        self,
        raw_anomalies: List[Dict[str, Any]],
    ) -> List[CohortAnomaly]:
        anomalies: List[CohortAnomaly] = []
        for anomaly in raw_anomalies:
            title = anomaly.get("title")
            description = anomaly.get("description")
            if not title or not description:
                continue
            anomalies.append(
                CohortAnomaly(
                    title=str(title),
                    description=str(description),
                    affected_vin_count=int(
                        anomaly.get("affected_vin_count", 1)
                    ),
                    severity=str(anomaly.get("severity", "MEDIUM")),
                    related_signals=anomaly.get("related_signals", []),
                )
            )
        return anomalies

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
