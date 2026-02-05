"""
GenAI Interpreter Service.

Central orchestration layer coordinating:
- predictive mart loading
- multi-agent GenAI interpretation
- VIN and cohort explanation workflows
- controlled conversational explanations (chat)

This service is the ONLY layer allowed to invoke GenAI agents.
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


class GenAIInterpreterService:
    """
    Orchestrates all GenAI interpretation workflows.

    Responsibilities:
    - VIN-level interpretation
    - Cohort-level interpretation
    - Action Pack assembly
    - Controlled chat-based explanations
    """

    def __init__(self, *, model_version: str = "v1") -> None:
        self._config = load_config()
        self._model_version = model_version

        self._mart_loader = MartLoader()
        self._vin_agent = VinExplainerAgent(model_version=model_version)
        self._cohort_agent = CohortBriefAgent(model_version=model_version)
        self._evidence_agent = EvidenceAgent()

    # ------------------------------------------------------------------
    # VIN Flow
    # ------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # Cohort Flow
    # ------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # Action Pack Assembly
    # ------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # Chat / Conversational Explanation (NEW)
    # ------------------------------------------------------------------

    def generate_chat_reply(
        self,
        *,
        user_message: str,
        context: Dict[str, Any] | None = None,
        request_id: str | None = None,
    ) -> str:
        """
        Generate a bounded, explainability-focused chat reply.

        This method is intentionally conservative:
        - No free-form reasoning
        - No access to raw telemetry
        - No speculative answers

        Intended for dashboard explainability only.
        """

        set_request_id(request_id)

        log_event(
            logger,
            "Generating GenAI chat reply",
            extra={
                "message_length": len(user_message),
                "context_keys": list(context.keys()) if context else [],
            },
        )

        # Simple routing heuristic (expand later if needed)
        if context and "vin" in context:
            reply = self._vin_agent.answer_question(
                question=user_message,
                context=context,
            )
        elif context and "cohort_id" in context:
            reply = self._cohort_agent.answer_question(
                question=user_message,
                context=context,
            )
        else:
            # Generic explainability mode
            reply = (
                "I can help explain predictive maintenance signals, "
                "risk levels, and recommended actions. "
                "Please reference a VIN or cohort for more specific insight."
            )

        log_event(
            logger,
            "GenAI chat reply generated",
            extra={"reply_length": len(reply)},
        )

        return reply
