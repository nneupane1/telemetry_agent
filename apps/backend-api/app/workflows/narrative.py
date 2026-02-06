"""
LangChain-backed narrative helpers with deterministic fallback.
"""

from __future__ import annotations

import inspect
import re
from typing import Any, Dict, List, Optional

from app.utils.config import load_config
from app.utils.logger import get_logger, log_event

logger = get_logger(__name__)


class NarrativeComposer:
    """
    Composes concise explanations from structured evidence.

    If LangChain and an LLM provider are available, prompts can be routed
    through the model. If not, deterministic templates are used.
    """

    def __init__(self) -> None:
        self._config = load_config()
        self._prompt_cls = None
        self._output_parser = None
        self._llm_chain = None
        self._llm_enabled = False

        try:
            from langchain.prompts import ChatPromptTemplate
            from langchain_core.output_parsers import StrOutputParser

            self._prompt_cls = ChatPromptTemplate
            self._output_parser = StrOutputParser()
        except Exception:
            log_event(
                logger,
                "LangChain prompt runtime unavailable, using deterministic templates",
            )
            return

        llm_cfg = self._config.llm
        if llm_cfg.provider == "none" or llm_cfg.openai is None:
            return
        if llm_cfg.provider not in {"openai", "openai_compatible"}:
            log_event(
                logger,
                "Unsupported LLM provider configured, using deterministic templates",
                extra={"provider": llm_cfg.provider},
            )
            return

        try:
            from langchain_openai import ChatOpenAI
        except Exception:
            log_event(
                logger,
                "langchain-openai unavailable, using deterministic templates",
            )
            return

        model_kwargs: Dict[str, Any] = {}
        if llm_cfg.openai.base_url:
            init_params = inspect.signature(ChatOpenAI.__init__).parameters
            if "base_url" in init_params:
                model_kwargs["base_url"] = llm_cfg.openai.base_url
            elif "openai_api_base" in init_params:
                model_kwargs["openai_api_base"] = llm_cfg.openai.base_url

        model = ChatOpenAI(
            api_key=llm_cfg.openai.api_key.get_secret_value(),
            model=llm_cfg.openai.model,
            temperature=llm_cfg.openai.temperature,
            max_tokens=llm_cfg.openai.max_tokens,
            **model_kwargs,
        )

        prompt = self._prompt_cls.from_messages(
            [
                (
                    "system",
                    "You are a predictive-maintenance explainer. "
                    "Use only provided evidence. Do not invent diagnostics.",
                ),
                (
                    "human",
                    "Entity: {entity}\n"
                    "Risk: {risk}\n"
                    "Top signals:\n{signals}\n"
                    "Write 2 concise sentences for control-room operators.",
                ),
            ]
        )
        self._llm_chain = prompt | model | self._output_parser
        self._llm_enabled = True

    def compose_vin_summary(
        self,
        *,
        vin: str,
        risk_level: str,
        evidence: List[Dict[str, Any]],
    ) -> str:
        top = self._format_top_signals(evidence)

        if self._llm_enabled and self._llm_chain is not None:
            try:
                return self._llm_chain.invoke(
                    {
                        "entity": f"VIN {vin}",
                        "risk": risk_level,
                        "signals": top,
                    }
                )
            except Exception:
                log_event(
                    logger,
                    "LLM summary generation failed, falling back to deterministic mode",
                )

        if risk_level == "HIGH":
            return (
                f"VIN {vin} shows multiple high-confidence predictive anomalies. "
                f"Dominant signals: {top}."
            )
        if risk_level == "ELEVATED":
            return (
                f"VIN {vin} shows elevated predictive risk with active anomaly signals. "
                f"Dominant signals: {top}."
            )
        return (
            f"VIN {vin} currently has no high-confidence anomaly cluster. "
            f"Observed signals: {top}."
        )

    def compose_cohort_summary(
        self,
        *,
        cohort_id: str,
        high_anomaly_count: int,
        total_anomaly_count: int,
        top_metrics: List[Dict[str, Any]],
    ) -> str:
        metrics_text = ", ".join(
            f"{m.get('name')}={m.get('value')}" for m in top_metrics[:3]
        ) or "no dominant metrics"

        risk = "HIGH" if high_anomaly_count > 0 else "ELEVATED" if total_anomaly_count > 0 else "LOW"

        if self._llm_enabled and self._llm_chain is not None:
            try:
                return self._llm_chain.invoke(
                    {
                        "entity": f"Cohort {cohort_id}",
                        "risk": risk,
                        "signals": metrics_text,
                    }
                )
            except Exception:
                log_event(
                    logger,
                    "LLM cohort summary generation failed, using fallback text",
                )

        if high_anomaly_count > 0:
            return (
                f"Cohort {cohort_id} has high-severity anomaly concentration requiring immediate triage. "
                f"Key metrics: {metrics_text}."
            )
        if total_anomaly_count > 0:
            return (
                f"Cohort {cohort_id} has emerging anomaly patterns that should be monitored. "
                f"Key metrics: {metrics_text}."
            )
        return (
            f"Cohort {cohort_id} remains stable with no significant anomaly concentration. "
            f"Key metrics: {metrics_text}."
        )

    def compose_chat_reply(
        self,
        *,
        user_message: str,
        context: Optional[Dict[str, Any]],
    ) -> str:
        context = context or {}
        entity = context.get("vin") or context.get("cohort_id") or "fleet"
        risk = context.get("risk_level") or "UNKNOWN"
        evidence = context.get("evidence_summary") or {}

        evidence_keys = ", ".join(sorted(evidence.keys())) if isinstance(evidence, dict) else "none"

        if self._llm_enabled and self._llm_chain is not None:
            try:
                return self._llm_chain.invoke(
                    {
                        "entity": str(entity),
                        "risk": str(risk),
                        "signals": f"user_question={user_message}; evidence_sources={evidence_keys}",
                    }
                )
            except Exception:
                log_event(
                    logger,
                    "LLM chat composition failed, using bounded fallback",
                )

        return (
            f"For {entity}, current risk context is {risk}. "
            f"Available evidence sources: {evidence_keys}. "
            "Ask about a specific signal or recommendation for more detail."
        )

    def compose_hybrid_chat_reply(
        self,
        *,
        user_message: str,
        context: Optional[Dict[str, Any]],
        deterministic_reply: str,
    ) -> str:
        """
        Select the best available chat response between deterministic and LLM candidates.

        The deterministic candidate is treated as the safety baseline.
        The LLM candidate is accepted only when it scores higher on bounded,
        context-grounded heuristics.
        """
        context = context or {}
        deterministic = (deterministic_reply or "").strip()
        if not deterministic:
            deterministic = self.compose_chat_reply(
                user_message=user_message,
                context=context,
            )

        deterministic_score = self._score_chat_reply(
            reply=deterministic,
            user_message=user_message,
            context=context,
        )

        llm_reply = self._compose_llm_chat_candidate(
            user_message=user_message,
            context=context,
            deterministic_seed=deterministic,
        )
        if llm_reply is None:
            return deterministic

        llm_score = self._score_chat_reply(
            reply=llm_reply,
            user_message=user_message,
            context=context,
        )

        if llm_score > deterministic_score:
            log_event(
                logger,
                "Hybrid chat selected LLM candidate",
                extra={
                    "deterministic_score": deterministic_score,
                    "llm_score": llm_score,
                },
            )
            return llm_reply

        log_event(
            logger,
            "Hybrid chat selected deterministic candidate",
            extra={
                "deterministic_score": deterministic_score,
                "llm_score": llm_score,
            },
        )
        return deterministic

    @staticmethod
    def _format_top_signals(evidence: List[Dict[str, Any]]) -> str:
        if not evidence:
            return "none"

        ranked = sorted(
            evidence,
            key=lambda ev: float(ev.get("confidence", 0.0)),
            reverse=True,
        )
        top = ranked[:3]
        return ", ".join(
            f"{ev.get('signal_code')} ({int(float(ev.get('confidence', 0.0)) * 100)}%)"
            for ev in top
        )

    def _compose_llm_chat_candidate(
        self,
        *,
        user_message: str,
        context: Dict[str, Any],
        deterministic_seed: str,
    ) -> Optional[str]:
        if not self._llm_enabled or self._llm_chain is None:
            return None

        entity = context.get("vin") or context.get("cohort_id") or "fleet"
        risk = context.get("risk_level") or "UNKNOWN"
        evidence = context.get("evidence_summary") or {}
        evidence_keys = (
            ", ".join(sorted(evidence.keys()))
            if isinstance(evidence, dict) and evidence
            else "none"
        )

        signals = (
            f"user_question={user_message}; "
            f"evidence_sources={evidence_keys}; "
            f"deterministic_baseline={deterministic_seed}"
        )
        try:
            return self._llm_chain.invoke(
                {
                    "entity": str(entity),
                    "risk": str(risk),
                    "signals": signals,
                }
            )
        except Exception:
            log_event(
                logger,
                "LLM hybrid candidate generation failed; keeping deterministic reply",
            )
            return None

    @staticmethod
    def _score_chat_reply(
        *,
        reply: str,
        user_message: str,
        context: Dict[str, Any],
    ) -> int:
        score = 0
        text = (reply or "").strip()
        if not text:
            return -100

        length = len(text)
        if 80 <= length <= 450:
            score += 2
        elif length > 700:
            score -= 2

        entity = str(context.get("vin") or context.get("cohort_id") or "").strip()
        if entity and entity.lower() in text.lower():
            score += 1

        risk_level = context.get("risk_level")
        if isinstance(risk_level, str) and risk_level.strip():
            if risk_level.lower() in text.lower():
                score += 2
            else:
                score -= 2

        evidence = context.get("evidence_summary")
        if isinstance(evidence, dict) and evidence:
            mentioned = 0
            for key in evidence.keys():
                if str(key).lower() in text.lower():
                    mentioned += 1
            if mentioned > 0:
                score += 2
            else:
                score -= 1

        anomaly_count = context.get("anomaly_count")
        if isinstance(anomaly_count, int):
            if str(anomaly_count) in text:
                score += 1

        recommendations = context.get("recommendations")
        if isinstance(recommendations, list):
            rec_count = len(recommendations)
            if str(rec_count) in text:
                score += 1

        question_tokens = [
            token.lower()
            for token in re.findall(r"[A-Za-z]{4,}", user_message)
        ]
        if question_tokens:
            overlap = [
                tok for tok in question_tokens
                if tok in text.lower()
            ]
            if overlap:
                score += 1

        speculative_markers = [
            "maybe",
            "probably",
            "might",
            "i guess",
            "i think",
            "likely",
        ]
        for marker in speculative_markers:
            if marker in text.lower():
                score -= 2

        return score
