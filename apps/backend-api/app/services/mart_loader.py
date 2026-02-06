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
from typing import Any, Dict, List, Optional, Type

from pydantic import BaseModel, Field, ValidationError, root_validator

from app.utils.config import load_config
from app.utils.databricks_conn import DatabricksClient
from app.utils.logger import get_logger, log_event

logger = get_logger(__name__)


class MartLoaderError(RuntimeError):
    pass


VIN_PATTERN = re.compile(r"^[A-HJ-NPR-Z0-9]{5,32}$")
COHORT_PATTERN = re.compile(r"^[A-Za-z0-9_.:-]{2,128}$")


class _SampleVINEntrySchema(BaseModel):
    vin: str = Field(..., min_length=5, max_length=32)
    mh: List[Dict[str, Any]] = Field(default_factory=list)
    mp: List[Dict[str, Any]] = Field(default_factory=list)
    fim: List[Dict[str, Any]] = Field(default_factory=list)

    class Config:
        extra = "ignore"


class _SampleCohortEntrySchema(BaseModel):
    cohort_id: str = Field(..., min_length=2, max_length=128)
    metrics: List[Dict[str, Any]] = Field(default_factory=list)
    anomalies: List[Dict[str, Any]] = Field(default_factory=list)
    description: Optional[str] = None

    class Config:
        extra = "ignore"


class _SamplePayloadSchema(BaseModel):
    vins: List[_SampleVINEntrySchema] = Field(default_factory=list)
    cohorts: List[_SampleCohortEntrySchema] = Field(default_factory=list)

    class Config:
        extra = "ignore"


class _MHRowSchema(BaseModel):
    hi_code: Optional[str] = None
    signal_code: Optional[str] = None
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    trigger_probability: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    rootcause_probability: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    observed_at: Optional[Any] = None
    trigger_time: Optional[Any] = None
    event_time: Optional[Any] = None

    class Config:
        extra = "allow"

    @root_validator
    def _validate_mh_row(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if not (values.get("hi_code") or values.get("signal_code")):
            raise ValueError("MH row must include hi_code or signal_code")
        if (
            values.get("confidence") is None
            and values.get("trigger_probability") is None
            and values.get("rootcause_probability") is None
        ):
            raise ValueError("MH row must include a confidence/probability value")
        if (
            values.get("observed_at") is None
            and values.get("trigger_time") is None
            and values.get("event_time") is None
        ):
            raise ValueError("MH row must include a telemetry timestamp")
        return values


class _MPRowSchema(BaseModel):
    signal_code: Optional[str] = None
    trigger_code: Optional[str] = None
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    trigger_probability: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    observed_at: Optional[Any] = None
    trigger_time: Optional[Any] = None
    event_time: Optional[Any] = None

    class Config:
        extra = "allow"

    @root_validator
    def _validate_mp_row(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if not (values.get("signal_code") or values.get("trigger_code")):
            raise ValueError("MP row must include signal_code or trigger_code")
        if values.get("confidence") is None and values.get("trigger_probability") is None:
            raise ValueError("MP row must include confidence or trigger_probability")
        if (
            values.get("trigger_time") is None
            and values.get("observed_at") is None
            and values.get("event_time") is None
        ):
            raise ValueError("MP row must include a telemetry timestamp")
        return values


class _FIMRowSchema(BaseModel):
    signal_code: Optional[str] = None
    rootcause_code: Optional[str] = None
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    rootcause_probability: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    observed_at: Optional[Any] = None
    trigger_time: Optional[Any] = None
    event_time: Optional[Any] = None

    class Config:
        extra = "allow"

    @root_validator
    def _validate_fim_row(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if not (values.get("signal_code") or values.get("rootcause_code")):
            raise ValueError("FIM row must include signal_code or rootcause_code")
        if values.get("confidence") is None and values.get("rootcause_probability") is None:
            raise ValueError("FIM row must include confidence or rootcause_probability")
        if (
            values.get("observed_at") is None
            and values.get("trigger_time") is None
            and values.get("event_time") is None
        ):
            raise ValueError("FIM row must include a telemetry timestamp")
        return values


class _CohortMetricRowSchema(BaseModel):
    metric_name: Optional[str] = None
    name: Optional[str] = None
    metric_value: Optional[float] = None
    value: Optional[float] = None
    unit: Optional[str] = None
    description: Optional[str] = None

    class Config:
        extra = "allow"

    @root_validator
    def _validate_metric_row(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if not (values.get("metric_name") or values.get("name")):
            raise ValueError("Metric row must include metric_name or name")
        if values.get("metric_value") is None and values.get("value") is None:
            raise ValueError("Metric row must include metric_value or value")
        return values


class _CohortAnomalyRowSchema(BaseModel):
    title: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    affected_vin_count: int = Field(..., ge=0)
    severity: str = Field(..., min_length=1)
    related_signals: List[str] = Field(default_factory=list)

    class Config:
        extra = "allow"


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
            rows = self._sample_vin_rows(vin).get("mh", [])
            return self._validate_rows(
                rows,
                schema=_MHRowSchema,
                dataset_name="mh_snapshot",
            )

        table = self._qualified_table(self._config.data.mart_mh_table)
        query = (
            "SELECT * "
            f"FROM {table} "
            f"WHERE vin = '{self._escape_literal(vin)}' "
            "ORDER BY observed_at DESC"
        )
        rows = self._execute(query, query_tag="mh_snapshot")
        return self._validate_rows(
            rows,
            schema=_MHRowSchema,
            dataset_name="mh_snapshot",
        )

    def load_mp_triggers(self, vin: str) -> List[Dict[str, Any]]:
        vin = self._normalize_vin(vin)
        if self._config.data.source == "sample":
            rows = self._sample_vin_rows(vin).get("mp", [])
            return self._validate_rows(
                rows,
                schema=_MPRowSchema,
                dataset_name="mp_triggers",
            )

        table = self._qualified_table(self._config.data.mart_mp_table)
        query = (
            "SELECT * "
            f"FROM {table} "
            f"WHERE vin = '{self._escape_literal(vin)}' "
            "ORDER BY trigger_time DESC"
        )
        rows = self._execute(query, query_tag="mp_triggers")
        return self._validate_rows(
            rows,
            schema=_MPRowSchema,
            dataset_name="mp_triggers",
        )

    def load_fim_root_causes(self, vin: str) -> List[Dict[str, Any]]:
        vin = self._normalize_vin(vin)
        if self._config.data.source == "sample":
            rows = self._sample_vin_rows(vin).get("fim", [])
            return self._validate_rows(
                rows,
                schema=_FIMRowSchema,
                dataset_name="fim_rootcause",
            )

        table = self._qualified_table(self._config.data.mart_fim_table)
        query = (
            "SELECT * "
            f"FROM {table} "
            f"WHERE vin = '{self._escape_literal(vin)}' "
            "ORDER BY observed_at DESC"
        )
        rows = self._execute(query, query_tag="fim_rootcause")
        return self._validate_rows(
            rows,
            schema=_FIMRowSchema,
            dataset_name="fim_rootcause",
        )

    # -----------------------------------------------------------------
    # Cohort-level marts
    # -----------------------------------------------------------------

    def load_cohort_metrics(self, cohort_id: str) -> List[Dict[str, Any]]:
        cohort_id = self._normalize_cohort(cohort_id)
        if self._config.data.source == "sample":
            rows = self._sample_cohort_rows(cohort_id).get("metrics", [])
            return self._validate_rows(
                rows,
                schema=_CohortMetricRowSchema,
                dataset_name="cohort_metrics",
            )

        table = self._qualified_table(self._config.data.mart_cohort_metrics_table)
        query = (
            "SELECT * "
            f"FROM {table} "
            f"WHERE cohort_id = '{self._escape_literal(cohort_id)}'"
        )
        rows = self._execute(query, query_tag="cohort_metrics")
        return self._validate_rows(
            rows,
            schema=_CohortMetricRowSchema,
            dataset_name="cohort_metrics",
        )

    def load_cohort_anomalies(self, cohort_id: str) -> List[Dict[str, Any]]:
        cohort_id = self._normalize_cohort(cohort_id)
        if self._config.data.source == "sample":
            rows = self._sample_cohort_rows(cohort_id).get("anomalies", [])
            return self._validate_rows(
                rows,
                schema=_CohortAnomalyRowSchema,
                dataset_name="cohort_anomalies",
            )

        table = self._qualified_table(self._config.data.mart_cohort_anomalies_table)
        query = (
            "SELECT * "
            f"FROM {table} "
            f"WHERE cohort_id = '{self._escape_literal(cohort_id)}' "
            "ORDER BY severity DESC"
        )
        rows = self._execute(query, query_tag="cohort_anomalies")
        return self._validate_rows(
            rows,
            schema=_CohortAnomalyRowSchema,
            dataset_name="cohort_anomalies",
        )

    def list_cohorts(self) -> List[Dict[str, str | None]]:
        if self._config.data.source == "sample":
            cohorts = self._sample_data().get("cohorts", [])
            if not isinstance(cohorts, list):
                raise MartLoaderError("Sample data 'cohorts' must be a list")
            return self._normalize_cohort_items(cohorts)

        metrics_table = self._qualified_table(self._config.data.mart_cohort_metrics_table)
        anomalies_table = self._qualified_table(self._config.data.mart_cohort_anomalies_table)
        query = (
            "SELECT cohort_id "
            "FROM ("
            f"SELECT cohort_id FROM {metrics_table} "
            "UNION "
            f"SELECT cohort_id FROM {anomalies_table}"
            ") AS cohort_registry "
            "WHERE cohort_id IS NOT NULL "
            "ORDER BY cohort_id"
        )
        rows = self._execute(query, query_tag="cohort_list")
        return self._normalize_cohort_items(rows)

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

        try:
            _SamplePayloadSchema.parse_obj(data)
        except ValidationError as exc:
            raise MartLoaderError(
                "Sample data does not match expected ingestion schema"
            ) from exc

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

    def _normalize_cohort_items(
        self,
        rows: List[Dict[str, Any]],
    ) -> List[Dict[str, str | None]]:
        unique: List[Dict[str, str | None]] = []
        seen_ids = set()

        for idx, row in enumerate(rows):
            if not isinstance(row, dict):
                self._handle_invalid_row(
                    dataset_name="cohort_list",
                    row_index=idx,
                    reason="Row must be an object",
                )
                continue

            raw_cohort_id = self._get_case_insensitive(row, "cohort_id")
            if raw_cohort_id is None:
                self._handle_invalid_row(
                    dataset_name="cohort_list",
                    row_index=idx,
                    reason="Missing cohort_id",
                )
                continue

            try:
                cohort_id = self._normalize_cohort(str(raw_cohort_id))
            except MartLoaderError as exc:
                self._handle_invalid_row(
                    dataset_name="cohort_list",
                    row_index=idx,
                    reason=str(exc),
                )
                continue

            if cohort_id in seen_ids:
                continue
            seen_ids.add(cohort_id)

            description_raw = self._get_case_insensitive(row, "description")
            if description_raw is None:
                description_raw = self._get_case_insensitive(row, "cohort_description")

            unique.append(
                {
                    "cohort_id": cohort_id,
                    "cohort_description": (
                        str(description_raw).strip()
                        if isinstance(description_raw, str) and description_raw.strip()
                        else None
                    ),
                }
            )

        return unique

    def _validate_rows(
        self,
        rows: List[Dict[str, Any]],
        *,
        schema: Type[BaseModel],
        dataset_name: str,
    ) -> List[Dict[str, Any]]:
        valid_rows: List[Dict[str, Any]] = []
        for idx, row in enumerate(rows):
            if not isinstance(row, dict):
                self._handle_invalid_row(
                    dataset_name=dataset_name,
                    row_index=idx,
                    reason="Row must be an object",
                )
                continue
            try:
                normalized = schema.parse_obj(row).dict(exclude_none=True)
                valid_rows.append(normalized)
            except ValidationError as exc:
                reason = exc.errors()[0].get("msg", "Schema validation failed")
                self._handle_invalid_row(
                    dataset_name=dataset_name,
                    row_index=idx,
                    reason=reason,
                )

        return valid_rows

    def _handle_invalid_row(
        self,
        *,
        dataset_name: str,
        row_index: int,
        reason: str,
    ) -> None:
        strict_validation = self._config.features.strict_validation
        if strict_validation:
            raise MartLoaderError(
                f"Invalid mart data for {dataset_name} at row {row_index}: {reason}"
            )

        log_event(
            logger,
            "Invalid mart row dropped",
            extra={
                "dataset_name": dataset_name,
                "row_index": row_index,
                "reason": reason,
            },
        )

    @staticmethod
    def _get_case_insensitive(row: Dict[str, Any], key: str) -> Any:
        if key in row:
            return row[key]

        key_lc = key.lower()
        for row_key, row_value in row.items():
            if str(row_key).lower() == key_lc:
                return row_value
        return None

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
