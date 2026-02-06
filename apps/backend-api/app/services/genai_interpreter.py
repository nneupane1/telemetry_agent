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
from app.services.reference_loader import ReferenceLoader
from app.utils.config import load_config
from app.utils.logger import get_logger, log_event, set_request_id
from app.workflows.graph_runner import GraphRunner

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
        # Config is optional at construction time to keep local unit tests
        # import-safe when env/secrets are not present.
        try:
            self._config = load_config()
        except Exception:
            self._config = None
        self._model_version = model_version

        self._mart_loader = MartLoader()
        self._reference_loader = ReferenceLoader()
        self._vin_agent = VinExplainerAgent(model_version=model_version)
        self._cohort_agent = CohortBriefAgent(model_version=model_version)
        self._evidence_agent = EvidenceAgent()
        self._graph_runner = GraphRunner(
            vin_agent=self._vin_agent,
            cohort_agent=self._cohort_agent,
            evidence_agent=self._evidence_agent,
            model_version=model_version,
        )

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

        workflow_result = self._graph_runner.run_vin(
            vin=vin,
            mh_signals=mh,
            mp_signals=mp,
            fim_signals=fim,
            reference_map=reference_map,
        )
        if workflow_result.vin_interpretation is None:
            raise RuntimeError("VIN workflow did not return an interpretation")
        interpretation = workflow_result.vin_interpretation

        consolidated_evidence = workflow_result.evidence_summary or self._evidence_agent.consolidate(
            evidence=[
                ev
                for rec in interpretation.recommendations
                for ev in rec.evidence
            ]
        )

        interpretation = interpretation.copy(
            update={"evidence_summary": consolidated_evidence}
        )

        log_event(
            logger,
            "VIN interpretation workflow completed",
            extra={
                "vin": vin,
                "risk_level": interpretation.risk_level,
                "evidence_sources": list(consolidated_evidence.keys()),
                "langgraph_enabled": self._graph_runner.langgraph_enabled,
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

        workflow_result = self._graph_runner.run_cohort(
            cohort_id=cohort_id,
            metrics=metrics,
            anomalies=anomalies,
            cohort_description=cohort_description,
        )
        if workflow_result.cohort_interpretation is None:
            raise RuntimeError("Cohort workflow did not return an interpretation")
        interpretation = workflow_result.cohort_interpretation

        log_event(
            logger,
            "Cohort interpretation workflow completed",
            extra={
                "cohort_id": cohort_id,
                "anomaly_count": len(interpretation.anomalies),
                "langgraph_enabled": self._graph_runner.langgraph_enabled,
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
            if "risk_level" not in context:
                try:
                    vin_data = self.interpret_vin(
                        vin=context["vin"],
                        reference_map=self._reference_loader.load_reference_map(),
                        request_id=request_id,
                    )
                    context = {
                        **context,
                        "risk_level": vin_data.risk_level,
                        "recommendations": [
                            rec.dict() for rec in vin_data.recommendations
                        ],
                        "evidence_summary": vin_data.evidence_summary,
                    }
                except Exception:
                    # Keep chat resilient even if interpretation lookup fails.
                    pass
            deterministic_reply = self._vin_agent.answer_question(
                question=user_message,
                context=context,
            )
            reply = self._graph_runner.compose_chat_reply(
                user_message=user_message,
                context=context,
                deterministic_reply=deterministic_reply,
            )
        elif context and "cohort_id" in context:
            if "anomaly_count" not in context:
                try:
                    cohort_data = self.interpret_cohort(
                        cohort_id=context["cohort_id"],
                        request_id=request_id,
                    )
                    context = {
                        **context,
                        "anomaly_count": len(cohort_data.anomalies),
                        "risk_distribution": cohort_data.risk_distribution,
                    }
                except Exception:
                    pass
            deterministic_reply = self._cohort_agent.answer_question(
                question=user_message,
                context=context,
            )
            reply = self._graph_runner.compose_chat_reply(
                user_message=user_message,
                context=context,
                deterministic_reply=deterministic_reply,
            )
        else:
            reply = self._graph_runner.compose_chat_reply(
                user_message=user_message,
                context=context,
            )

        log_event(
            logger,
            "GenAI chat reply generated",
            extra={"reply_length": len(reply)},
        )

        return reply


# Backward-compatible alias used by legacy routers/tests.
GenAIInterpreter = GenAIInterpreterService
