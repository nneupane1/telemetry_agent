"""
Approval Store Service.

Persists operator approval decisions for Action Packs.
Designed to be storage-agnostic and auditable.
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List

from app.utils.logger import get_logger

logger = get_logger(__name__)


class ApprovalStore:
    """
    Simple approval persistence layer.

    Default implementation uses in-memory storage.
    Can be replaced with:
    - PostgreSQL
    - Delta table
    - Document store
    """

    def __init__(self) -> None:
        self._records: List[Dict] = []

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def record_decision(
        self,
        *,
        subject_type: str,
        subject_id: str,
        decision: str,
        comment: str,
        decided_by: str | None = None,
    ) -> Dict:
        """
        Persist an approval decision.
        """

        entry = {
            "subject_type": subject_type,
            "subject_id": subject_id,
            "decision": decision,
            "comment": comment,
            "decided_by": decided_by or "unknown",
            "timestamp": datetime.utcnow().isoformat(),
        }

        self._records.append(entry)

        logger.info(
            "Approval decision recorded",
            extra=entry,
        )

        return entry

    def list_decisions(
        self,
        *,
        subject_type: str | None = None,
        subject_id: str | None = None,
    ) -> List[Dict]:
        """
        Retrieve approval decisions with optional filtering.
        """

        results = self._records

        if subject_type:
            results = [
                r for r in results
                if r["subject_type"] == subject_type
            ]

        if subject_id:
            results = [
                r for r in results
                if r["subject_id"] == subject_id
            ]

        return results
