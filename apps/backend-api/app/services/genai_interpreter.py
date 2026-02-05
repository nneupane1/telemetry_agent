"""
GenAI Interpreter Service.

Central orchestration layer that coordinates data loading and agent
execution to produce VIN- and cohort-level interpretations.

Used by:
- API routers
- Batch jobs
- PDF / email pipelines
"""

from __future__ import annotations

from typing import Any, Dict

from app.agents.cohort_brief_agent import CohortBriefAgent
from app.agents.evidence_agent import EvidenceAgent
from app.agents.vin_explainer_agent import VinExplainerAgent
from app.models.action_pack import ActionPack
from app.models.cohort import CohortInterpretation
from app.models.vin import VinInterpretation
from app.services.mart_loader import MartLoader
from app.utils.config import load_config
from app.utils.logger import get_logger, log_event, set_request_id

logger = get_logger(__name__)


class GenAIInterpreter:
    """
    Orchestrates multi-agent interpretation workflows.
    """

    def __init__(self, *, model_version: str) -> None:
        self._config = load_config()
        self._model_version = model_version

        self._mart_loader = MartLoader()
        self._vin_agent = VinExplainerAgent(model_version=model_version)
        self._cohort_agent = CohortBriefAgent(model_version=model_version)
        self._evidence_agent = EvidenceAgent()

    # -----------------------------------------------------------------
    # VIN Flow
    # -----------------------------------------------------------------

    def interpret_vin(
        self,
        *,
        vin: str,
        reference_map: Dict[str, Dict[str, Any]],
        request_id: str | None = None,
    ) -> VinInterpretation:
        """
        End-to-end VIN interpretation workflow.
        """

        set_request_id(request_id)

        log_event(
            logger,
            "Starting VIN interpretation workflow",
            extra={"vin": vin},
        )

        mh = self._mart_loader.load_mh_snapshot(vin)
        mp = self._mart_loader.load_mp_triggers(vin)
        fim = self._mart_loader.load_fim_root_causes(vin)

        interpretation = self._vin_agent.explain(
            vin=vin,
            mh_signals=mh,
            mp_signals=mp,
            fim_signals=fim,
            reference_map=reference_map,
        )

        # Evidence consolidation (for audit / downstream use)
        consolidated_evidence = self._evidence_agent.consolidate(
            evidence=[
                ev
                for rec in interpretation.recommendations
                for ev in rec.evidence
            ]
        )

        log_event(
            logger,
            "VIN interpretation workflow completed",
            extra={
                "vin": vin,
                "risk_level": interpretation.risk_level,
                "evidence_sources": list(consolidated_evidence.keys()),
            },
        )

        return interpretation

    # -----------------------------------------------------------------
    # Cohort Flow
    # -----------------------------------------------------------------

    def interpret_cohort(
        self,
        *,
        cohort_id: str,
        cohort_description: str | None = None,
        request_id: str | None = None,
    ) -> CohortInterpretation:
        """
        End-to-end cohort interpretation workflow.
        """

        set_request_id(request_id)

        log_event(
            logger,
            "Starting cohort interpretation workflow",
            extra={"cohort_id": cohort_id},
        )

        metrics = self._mart_loader.load_cohort_metrics(cohort_id)
        anomalies = self._mart_loader.load_cohort_anomalies(cohort_id)

        interpretation = self._cohort_agent.explain(
            cohort_id=cohort_id,
            metrics=metrics,
            anomalies=anomalies,
            cohort_description=cohort_description,
        )

        log_event(
            logger,
            "Cohort interpretation workflow completed",
            extra={
                "cohort_id": cohort_id,
                "anomaly_count": len(interpretation.anomalies),
            },
        )

        return interpretation

    # -----------------------------------------------------------------
    # Action Pack Assembly
    # -----------------------------------------------------------------

    def build_action_pack(
        self,
        *,
        subject_type: str,
        subject_id: str,
        title: str,
        executive_summary: str,
        recommendations,
    ) -> ActionPack:
        """
        Assemble a delivery-ready Action Pack.
        """

        action_pack = ActionPack(
            action_pack_id=f"AP-{subject_id}",
            subject_type=subject_type,
            subject_id=subject_id,
            title=title,
            executive_summary=executive_summary,
            recommendations=recommendations,
            model_version=self._model_version,
        )

        log_event(
            logger,
            "Action Pack assembled",
            extra={
                "subject_type": subject_type,
                "subject_id": subject_id,
                "recommendation_count": len(recommendations),
            },
        )

        return action_pack
