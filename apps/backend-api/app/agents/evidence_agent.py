"""
Evidence Agent.

This agent consolidates, ranks, and explains evidence used in
VIN or cohort interpretations to ensure transparency, auditability,
and trust in GenAI-assisted decisions.

Used by:
- GenAI interpreter service
- Approval workflows
- PDF / evidence review screens
"""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, List

from app.models.vin import EvidenceItem
from app.utils.logger import (
    get_logger,
    log_event,
    set_agent,
)

logger = get_logger(__name__)


class EvidenceAgent:
    """
    Agent responsible for evidence consolidation and justification.
    """

    def __init__(self) -> None:
        pass

    # -----------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------

    def consolidate(
        self,
        *,
        evidence: List[EvidenceItem],
    ) -> Dict[str, Dict[str, object]]:
        """
        Consolidate evidence into an auditable structure grouped
        by source model and signal.
        """

        set_agent("evidence_agent")

        log_event(
            logger,
            "Starting evidence consolidation",
            extra={"evidence_count": len(evidence)},
        )

        grouped: Dict[str, Dict[str, List[EvidenceItem]]] = defaultdict(
            lambda: defaultdict(list)
        )

        for ev in evidence:
            grouped[ev.source_model][ev.signal_code].append(ev)

        consolidated: Dict[str, Dict[str, object]] = {}

        for source_model, signals in grouped.items():
            consolidated[source_model] = {}

            for signal_code, items in signals.items():
                consolidated[source_model][signal_code] = {
                    "description": items[0].signal_description,
                    "occurrences": len(items),
                    "max_confidence": max(i.confidence for i in items),
                    "avg_confidence": sum(i.confidence for i in items)
                    / len(items),
                    "first_seen": min(i.observed_at for i in items),
                    "last_seen": max(i.observed_at for i in items),
                }

        log_event(
            logger,
            "Evidence consolidation completed",
            extra={"source_models": list(consolidated.keys())},
        )

        return consolidated
