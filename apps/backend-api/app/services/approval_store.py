"""
Approval Store Service.

Persists operator approval decisions for Action Packs.
Designed to be storage-agnostic and auditable.
"""

from __future__ import annotations

from datetime import datetime
import json
import os
from pathlib import Path
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
        self._path = self._resolve_store_path()
        self._load_from_disk()

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
        self._flush_to_disk()

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

    # ---------------------------------------------------------
    # Persistence helpers
    # ---------------------------------------------------------

    def _resolve_store_path(self) -> Path:
        raw = os.getenv("APPROVAL_STORE_FILE", ".approval_store.json")
        path = Path(raw)
        if path.is_absolute():
            return path
        return Path.cwd() / path

    def _load_from_disk(self) -> None:
        if not self._path.exists():
            return
        try:
            payload = json.loads(self._path.read_text(encoding="utf-8"))
            if isinstance(payload, list):
                self._records = [row for row in payload if isinstance(row, dict)]
        except Exception:
            logger.warning("Failed to load approval store from disk")

    def _flush_to_disk(self) -> None:
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            self._path.write_text(
                json.dumps(self._records, indent=2),
                encoding="utf-8",
            )
        except Exception:
            logger.warning("Failed to persist approval store to disk")
