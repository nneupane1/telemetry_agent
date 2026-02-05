"""
Mart Loader Service.

This module is the single source of truth for reading predictive
maintenance data from Databricks marts and returning normalized,
agent-ready records.

Used by:
- GenAI agents
- API services
- Cohort aggregation logic
"""

from __future__ import annotations

from typing import Any, Dict, List

from app.utils.databricks_conn import DatabricksClient
from app.utils.logger import get_logger, log_event

logger = get_logger(__name__)


class MartLoaderError(RuntimeError):
    pass


class MartLoader:
    """
    Read-only access layer for predictive marts.
    """

    def __init__(self) -> None:
        self._client = DatabricksClient()

    # -----------------------------------------------------------------
    # VIN-level marts
    # -----------------------------------------------------------------

    def load_mh_snapshot(self, vin: str) -> List[Dict[str, Any]]:
        """
        Load Machine Health (MH) snapshot data for a VIN.
        """

        query = f"""
        SELECT *
        FROM mart_mh_hi_snapshot_daily
        WHERE vin = '{vin}'
        ORDER BY observed_at DESC
        """

        return self._execute(query, query_tag="mh_snapshot")

    def load_mp_triggers(self, vin: str) -> List[Dict[str, Any]]:
        """
        Load Maintenance Prediction (MP) trigger events for a VIN.
        """

        query = f"""
        SELECT *
        FROM mart_mp_triggers_daily
        WHERE vin = '{vin}'
        ORDER BY trigger_time DESC
        """

        return self._execute(query, query_tag="mp_triggers")

    def load_fim_root_causes(self, vin: str) -> List[Dict[str, Any]]:
        """
        Load Failure Impact Model (FIM) root cause signals for a VIN.
        """

        query = f"""
        SELECT *
        FROM mart_fim_rootcause_daily
        WHERE vin = '{vin}'
        ORDER BY observed_at DESC
        """

        return self._execute(query, query_tag="fim_rootcause")

    # -----------------------------------------------------------------
    # Cohort-level marts
    # -----------------------------------------------------------------

    def load_cohort_metrics(self, cohort_id: str) -> List[Dict[str, Any]]:
        """
        Load aggregated cohort metrics.
        """

        query = f"""
        SELECT *
        FROM mart_cohort_metrics_daily
        WHERE cohort_id = '{cohort_id}'
        """

        return self._execute(query, query_tag="cohort_metrics")

    def load_cohort_anomalies(self, cohort_id: str) -> List[Dict[str, Any]]:
        """
        Load detected cohort-level anomalies.
        """

        query = f"""
        SELECT *
        FROM mart_cohort_anomalies_daily
        WHERE cohort_id = '{cohort_id}'
        ORDER BY severity DESC
        """

        return self._execute(query, query_tag="cohort_anomalies")

    # -----------------------------------------------------------------
    # Internal helpers
    # -----------------------------------------------------------------

    def _execute(self, query: str, *, query_tag: str) -> List[Dict[str, Any]]:
        """
        Execute a mart query and normalize rows into dicts.
        """

        try:
            columns, rows = self._client.execute_query(
                query,
                query_tag=query_tag,
            )

            records = [dict(zip(columns, row)) for row in rows]

            log_event(
                logger,
                "Mart query loaded",
                extra={
                    "query_tag": query_tag,
                    "row_count": len(records),
                },
            )

            return records

        except Exception as exc:
            raise MartLoaderError(
                f"Failed to load mart data ({query_tag})"
            ) from exc
