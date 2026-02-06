"""
Mart Loader Service.

Reads predictive telemetry from:
- Databricks Unity Catalog marts (production mode)
- local sample JSON (development fallback)
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List

from app.utils.config import load_config
from app.utils.databricks_conn import DatabricksClient
from app.utils.logger import get_logger, log_event

logger = get_logger(__name__)


class MartLoaderError(RuntimeError):
    pass


VIN_PATTERN = re.compile(r"^[A-HJ-NPR-Z0-9]{5,32}$")
COHORT_PATTERN = re.compile(r"^[A-Za-z0-9_.:-]{2,128}$")


class MartLoader:
    """
    Read-only access layer for predictive marts.
    """

    def __init__(self) -> None:
        self._config = load_config()
        self._client = DatabricksClient()
        self._sample_cache: Dict[str, Any] | None = None

    # -----------------------------------------------------------------
    # VIN-level marts
    # -----------------------------------------------------------------

    def load_mh_snapshot(self, vin: str) -> List[Dict[str, Any]]:
        vin = self._normalize_vin(vin)
        if self._config.data.source == "sample":
            return self._sample_vin_rows(vin).get("mh", [])

        table = self._qualified_table(self._config.data.mart_mh_table)
        query = (
            "SELECT * "
            f"FROM {table} "
            f"WHERE vin = '{self._escape_literal(vin)}' "
            "ORDER BY observed_at DESC"
        )
        return self._execute(query, query_tag="mh_snapshot")

    def load_mp_triggers(self, vin: str) -> List[Dict[str, Any]]:
        vin = self._normalize_vin(vin)
        if self._config.data.source == "sample":
            return self._sample_vin_rows(vin).get("mp", [])

        table = self._qualified_table(self._config.data.mart_mp_table)
        query = (
            "SELECT * "
            f"FROM {table} "
            f"WHERE vin = '{self._escape_literal(vin)}' "
            "ORDER BY trigger_time DESC"
        )
        return self._execute(query, query_tag="mp_triggers")

    def load_fim_root_causes(self, vin: str) -> List[Dict[str, Any]]:
        vin = self._normalize_vin(vin)
        if self._config.data.source == "sample":
            return self._sample_vin_rows(vin).get("fim", [])

        table = self._qualified_table(self._config.data.mart_fim_table)
        query = (
            "SELECT * "
            f"FROM {table} "
            f"WHERE vin = '{self._escape_literal(vin)}' "
            "ORDER BY observed_at DESC"
        )
        return self._execute(query, query_tag="fim_rootcause")

    # -----------------------------------------------------------------
    # Cohort-level marts
    # -----------------------------------------------------------------

    def load_cohort_metrics(self, cohort_id: str) -> List[Dict[str, Any]]:
        cohort_id = self._normalize_cohort(cohort_id)
        if self._config.data.source == "sample":
            return self._sample_cohort_rows(cohort_id).get("metrics", [])

        table = self._qualified_table(self._config.data.mart_cohort_metrics_table)
        query = (
            "SELECT * "
            f"FROM {table} "
            f"WHERE cohort_id = '{self._escape_literal(cohort_id)}'"
        )
        return self._execute(query, query_tag="cohort_metrics")

    def load_cohort_anomalies(self, cohort_id: str) -> List[Dict[str, Any]]:
        cohort_id = self._normalize_cohort(cohort_id)
        if self._config.data.source == "sample":
            return self._sample_cohort_rows(cohort_id).get("anomalies", [])

        table = self._qualified_table(self._config.data.mart_cohort_anomalies_table)
        query = (
            "SELECT * "
            f"FROM {table} "
            f"WHERE cohort_id = '{self._escape_literal(cohort_id)}' "
            "ORDER BY severity DESC"
        )
        return self._execute(query, query_tag="cohort_anomalies")

    # -----------------------------------------------------------------
    # Internal helpers
    # -----------------------------------------------------------------

    def _execute(self, query: str, *, query_tag: str) -> List[Dict[str, Any]]:
        try:
            columns, rows = self._client.execute_query(
                query,
                query_tag=query_tag,
            )
            records = [dict(zip(columns, row)) for row in rows]

            log_event(
                logger,
                "Mart query loaded",
                extra={"query_tag": query_tag, "row_count": len(records)},
            )

            return records
        except Exception as exc:
            raise MartLoaderError(
                f"Failed to load mart data ({query_tag})"
            ) from exc

    def _qualified_table(self, table_name: str) -> str:
        dbx = self._config.databricks
        if dbx is None:
            return table_name
        return f"{dbx.catalog}.{dbx.schema_name}.{table_name}"

    @staticmethod
    def _escape_literal(value: str) -> str:
        return value.replace("'", "''")

    @staticmethod
    def _normalize_vin(vin: str) -> str:
        normalized = vin.strip().upper()
        if not VIN_PATTERN.match(normalized):
            raise MartLoaderError("Invalid VIN format")
        return normalized

    @staticmethod
    def _normalize_cohort(cohort_id: str) -> str:
        normalized = cohort_id.strip()
        if not COHORT_PATTERN.match(normalized):
            raise MartLoaderError("Invalid cohort_id format")
        return normalized

    def _sample_data(self) -> Dict[str, Any]:
        if self._sample_cache is not None:
            return self._sample_cache

        sample_path = self._resolve_path(self._config.data.sample_file)
        if not sample_path.exists():
            raise MartLoaderError(
                f"Sample data file not found: {sample_path}"
            )

        with sample_path.open("r", encoding="utf-8-sig") as handle:
            data = json.load(handle)

        if not isinstance(data, dict):
            raise MartLoaderError("Sample data must be a JSON object")

        self._sample_cache = data
        return data

    def _sample_vin_rows(self, vin: str) -> Dict[str, Any]:
        vins = self._sample_data().get("vins", [])
        if not isinstance(vins, list):
            raise MartLoaderError("Sample data 'vins' must be a list")

        for item in vins:
            if str(item.get("vin", "")).upper() == vin:
                return item

        return {"mh": [], "mp": [], "fim": []}

    def _sample_cohort_rows(self, cohort_id: str) -> Dict[str, Any]:
        cohorts = self._sample_data().get("cohorts", [])
        if not isinstance(cohorts, list):
            raise MartLoaderError("Sample data 'cohorts' must be a list")

        for item in cohorts:
            if str(item.get("cohort_id", "")) == cohort_id:
                return item

        return {"metrics": [], "anomalies": []}

    @staticmethod
    def _resolve_path(path_value: str) -> Path:
        path = Path(path_value)
        if path.is_absolute() and path.exists():
            return path
        if path.exists():
            return path

        repo_root = Path(__file__).resolve().parents[4]
        candidate = repo_root / path_value
        if candidate.exists():
            return candidate

        return path
