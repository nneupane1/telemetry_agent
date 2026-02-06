"""
Graph-based orchestration layer.

Uses LangGraph as the primary orchestration runtime.
Deterministic sequential fallback is only used when explicitly enabled.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from app.models.cohort import CohortInterpretation
from app.models.vin import EvidenceItem, Recommendation, VinInterpretation
from app.utils.config import load_config
from app.utils.logger import get_logger, log_event
from app.workflows.narrative import NarrativeComposer

logger = get_logger(__name__)


@dataclass(frozen=True)
class WorkflowResult:
    vin_interpretation: Optional[VinInterpretation] = None
    cohort_interpretation: Optional[CohortInterpretation] = None
    evidence_summary: Optional[Dict[str, Dict[str, object]]] = None


class GraphRunner:
    def __init__(self, *, vin_agent, cohort_agent, evidence_agent, model_version: str) -> None:
        self._config = load_config()
        self._vin_agent = vin_agent
        self._cohort_agent = cohort_agent
        self._evidence_agent = evidence_agent
        self._model_version = model_version
        self._composer = NarrativeComposer()

        self._langgraph_available = False
        self._vin_graph = None
        self._cohort_graph = None

        if self._config.features.enable_langgraph:
            self._initialize_graphs()
        elif not self._config.features.allow_deterministic_fallback:
            raise RuntimeError(
                "FEATURE_LANGGRAPH=false is not allowed unless "
                "FEATURE_ALLOW_DETERMINISTIC_FALLBACK=true."
            )

        if (
            not self._config.features.allow_deterministic_fallback
            and not self._langgraph_available
        ):
            raise RuntimeError(
                "LangGraph orchestration is required but unavailable."
            )

    @property
    def langgraph_enabled(self) -> bool:
        return self._langgraph_available

    def run_vin(
        self,
        *,
        vin: str,
        mh_signals: List[Dict[str, Any]],
        mp_signals: List[Dict[str, Any]],
        fim_signals: List[Dict[str, Any]],
        reference_map: Dict[str, Dict[str, Any]],
    ) -> WorkflowResult:
        initial_state = {
            "vin": vin,
            "mh_signals": mh_signals,
            "mp_signals": mp_signals,
            "fim_signals": fim_signals,
            "reference_map": reference_map,
        }

        if self._vin_graph is None:
            if self._config.features.allow_deterministic_fallback:
                return self._run_vin_fallback(initial_state)
            raise RuntimeError("VIN graph is unavailable.")

        try:
            final_state = self._vin_graph.invoke(initial_state)
            return WorkflowResult(
                vin_interpretation=final_state.get("interpretation"),
                evidence_summary=final_state.get("evidence_summary"),
            )
        except Exception:
            if self._config.features.allow_deterministic_fallback:
                log_event(
                    logger,
                    "LangGraph VIN workflow failed, using deterministic fallback",
                )
                return self._run_vin_fallback(initial_state)
            raise

    def run_cohort(
        self,
        *,
        cohort_id: str,
        metrics: List[Dict[str, Any]],
        anomalies: List[Dict[str, Any]],
        cohort_description: Optional[str],
    ) -> WorkflowResult:
        initial_state = {
            "cohort_id": cohort_id,
            "cohort_description": cohort_description,
            "metrics_raw": metrics,
            "anomalies_raw": anomalies,
        }

        if self._cohort_graph is None:
            if self._config.features.allow_deterministic_fallback:
                return self._run_cohort_fallback(initial_state)
            raise RuntimeError("Cohort graph is unavailable.")

        try:
            final_state = self._cohort_graph.invoke(initial_state)
            return WorkflowResult(
                cohort_interpretation=final_state.get("interpretation")
            )
        except Exception:
            if self._config.features.allow_deterministic_fallback:
                log_event(
                    logger,
                    "LangGraph cohort workflow failed, using deterministic fallback",
                )
                return self._run_cohort_fallback(initial_state)
            raise

    def compose_chat_reply(
        self,
        *,
        user_message: str,
        context: Optional[Dict[str, Any]],
        deterministic_reply: Optional[str] = None,
    ) -> str:
        if deterministic_reply is not None:
            return self._composer.compose_hybrid_chat_reply(
                user_message=user_message,
                context=context,
                deterministic_reply=deterministic_reply,
            )
        return self._composer.compose_chat_reply(
            user_message=user_message,
            context=context,
        )

    def _initialize_graphs(self) -> None:
        try:
            from langgraph.graph import END, StateGraph
        except Exception as exc:
            log_event(
                logger,
                "LangGraph package unavailable",
            )
            if self._config.features.allow_deterministic_fallback:
                return
            raise RuntimeError(
                "langgraph package is required when deterministic fallback is disabled."
            ) from exc

        # VIN graph
        vin_graph = StateGraph(dict)
        vin_graph.add_node("build_evidence", self._node_vin_build_evidence)
        vin_graph.add_node("summarize", self._node_vin_summarize)
        vin_graph.add_node("recommend", self._node_vin_recommend)
        vin_graph.add_node("consolidate", self._node_vin_consolidate)
        vin_graph.add_node("assemble", self._node_vin_assemble)
        vin_graph.set_entry_point("build_evidence")
        vin_graph.add_edge("build_evidence", "summarize")
        vin_graph.add_edge("summarize", "recommend")
        vin_graph.add_edge("recommend", "consolidate")
        vin_graph.add_edge("consolidate", "assemble")
        vin_graph.add_edge("assemble", END)

        # Cohort graph
        cohort_graph = StateGraph(dict)
        cohort_graph.add_node("build_models", self._node_cohort_build_models)
        cohort_graph.add_node("summarize", self._node_cohort_summarize)
        cohort_graph.add_node("assemble", self._node_cohort_assemble)
        cohort_graph.set_entry_point("build_models")
        cohort_graph.add_edge("build_models", "summarize")
        cohort_graph.add_edge("summarize", "assemble")
        cohort_graph.add_edge("assemble", END)

        self._vin_graph = vin_graph.compile()
        self._cohort_graph = cohort_graph.compile()
        self._langgraph_available = True

        log_event(
            logger,
            "LangGraph workflows initialized",
            extra={"vin_graph": True, "cohort_graph": True},
        )

    # -------------------------- VIN Nodes --------------------------

    def _node_vin_build_evidence(self, state: Dict[str, Any]) -> Dict[str, Any]:
        evidence = self._vin_agent._build_evidence(
            state["mh_signals"],
            state["mp_signals"],
            state["fim_signals"],
            state["reference_map"],
        )
        return {"evidence": evidence}

    def _node_vin_summarize(self, state: Dict[str, Any]) -> Dict[str, Any]:
        summary, risk_level = self._vin_agent._generate_summary(state["evidence"])
        evidence_rows = [
            {
                "signal_code": ev.signal_code,
                "confidence": ev.confidence,
            }
            for ev in state["evidence"]
        ]
        summary = self._composer.compose_vin_summary(
            vin=state["vin"],
            risk_level=risk_level,
            evidence=evidence_rows,
        )
        return {"summary": summary, "risk_level": risk_level}

    def _node_vin_recommend(self, state: Dict[str, Any]) -> Dict[str, Any]:
        recommendations = self._vin_agent._generate_recommendations(state["evidence"])
        return {"recommendations": recommendations}

    def _node_vin_consolidate(self, state: Dict[str, Any]) -> Dict[str, Any]:
        evidence_summary = self._evidence_agent.consolidate(
            evidence=state["evidence"]
        )
        return {"evidence_summary": evidence_summary}

    def _node_vin_assemble(self, state: Dict[str, Any]) -> Dict[str, Any]:
        interpretation = VinInterpretation(
            vin=state["vin"],
            summary=state["summary"],
            risk_level=state["risk_level"],
            recommendations=state["recommendations"],
            model_version=self._model_version,
        )
        return {"interpretation": interpretation}

    # ------------------------ Cohort Nodes -------------------------

    def _node_cohort_build_models(self, state: Dict[str, Any]) -> Dict[str, Any]:
        metrics = self._cohort_agent._build_metrics(state["metrics_raw"])
        anomalies = self._cohort_agent._build_anomalies(state["anomalies_raw"])
        distribution = self._cohort_agent._risk_distribution(state["metrics_raw"])
        return {
            "metrics": metrics,
            "anomalies": anomalies,
            "risk_distribution": distribution,
        }

    def _node_cohort_summarize(self, state: Dict[str, Any]) -> Dict[str, Any]:
        summary = self._cohort_agent._generate_summary(
            state["metrics"],
            state["anomalies"],
        )
        high_count = len([a for a in state["anomalies"] if a.severity.upper() == "HIGH"])
        summary = self._composer.compose_cohort_summary(
            cohort_id=state["cohort_id"],
            high_anomaly_count=high_count,
            total_anomaly_count=len(state["anomalies"]),
            top_metrics=[{"name": m.name, "value": m.value} for m in state["metrics"]],
        )
        return {"summary": summary}

    def _node_cohort_assemble(self, state: Dict[str, Any]) -> Dict[str, Any]:
        interpretation = CohortInterpretation(
            cohort_id=state["cohort_id"],
            cohort_description=state.get("cohort_description"),
            summary=state["summary"],
            metrics=state["metrics"],
            anomalies=state["anomalies"],
            risk_distribution=state.get("risk_distribution"),
            model_version=self._model_version,
        )
        return {"interpretation": interpretation}

    # --------------------- Fallback Orchestration ------------------

    def _run_vin_fallback(self, state: Dict[str, Any]) -> WorkflowResult:
        evidence: List[EvidenceItem] = self._vin_agent._build_evidence(
            state["mh_signals"],
            state["mp_signals"],
            state["fim_signals"],
            state["reference_map"],
        )
        summary, risk_level = self._vin_agent._generate_summary(evidence)
        summary = self._composer.compose_vin_summary(
            vin=state["vin"],
            risk_level=risk_level,
            evidence=[
                {"signal_code": ev.signal_code, "confidence": ev.confidence}
                for ev in evidence
            ],
        )
        recommendations: List[Recommendation] = self._vin_agent._generate_recommendations(
            evidence
        )
        evidence_summary = self._evidence_agent.consolidate(evidence=evidence)

        interpretation = VinInterpretation(
            vin=state["vin"],
            summary=summary,
            risk_level=risk_level,
            recommendations=recommendations,
            model_version=self._model_version,
        )
        return WorkflowResult(
            vin_interpretation=interpretation,
            evidence_summary=evidence_summary,
        )

    def _run_cohort_fallback(self, state: Dict[str, Any]) -> WorkflowResult:
        metrics = self._cohort_agent._build_metrics(state["metrics_raw"])
        anomalies = self._cohort_agent._build_anomalies(state["anomalies_raw"])
        distribution = self._cohort_agent._risk_distribution(state["metrics_raw"])
        summary = self._cohort_agent._generate_summary(metrics, anomalies)
        summary = self._composer.compose_cohort_summary(
            cohort_id=state["cohort_id"],
            high_anomaly_count=len([a for a in anomalies if a.severity.upper() == "HIGH"]),
            total_anomaly_count=len(anomalies),
            top_metrics=[{"name": m.name, "value": m.value} for m in metrics],
        )

        interpretation = CohortInterpretation(
            cohort_id=state["cohort_id"],
            cohort_description=state.get("cohort_description"),
            summary=summary,
            metrics=metrics,
            anomalies=anomalies,
            risk_distribution=distribution,
            model_version=self._model_version,
        )
        return WorkflowResult(cohort_interpretation=interpretation)
