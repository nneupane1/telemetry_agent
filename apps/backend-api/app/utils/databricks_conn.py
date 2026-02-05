"""
Databricks / Unity Catalog connection utilities.

Principles:
- Read-only, auditable access
- Safe for multi-tenant Unity Catalog
- Explicit query tagging for forensic traceability
- Retry + timeout hardened
"""

from __future__ import annotations

import time
from contextlib import contextmanager
from typing import Generator, Optional

from databricks import sql

from app.utils.config import load_config
from app.utils.logger import get_logger, log_event

logger = get_logger(__name__)


class DatabricksConnectionError(RuntimeError):
    pass


class DatabricksClient:
    """
    Thin, safe wrapper around Databricks SQL connector.
    """

    def __init__(self) -> None:
        self._config = load_config().databricks

    @contextmanager
    def connect(
        self,
        *,
        query_tag: Optional[str] = None,
        retries: int = 3,
        retry_backoff: float = 1.5,
    ) -> Generator[sql.client.Connection, None, None]:
        """
        Context-managed Databricks SQL connection.
        Enforces retry, tagging, and clean teardown.
        """

        attempt = 0
        while True:
            try:
                conn = sql.connect(
                    server_hostname=self._config.host,
                    http_path=self._config.http_path,
                    access_token=self._config.token.get_secret_value(),
                    session_configuration={
                        "QUERY_TAGS": query_tag or "genai-predictive-platform",
                        "ANSI_MODE": "true",
                    },
                )

                log_event(
                    logger,
                    "Databricks connection established",
                    extra={"query_tag": query_tag},
                )

                yield conn
                conn.close()
                return

            except Exception as exc:
                attempt += 1
                if attempt >= retries:
                    raise DatabricksConnectionError(
                        "Failed to connect to Databricks SQL Warehouse"
                    ) from exc

                time.sleep(retry_backoff ** attempt)

    def execute_query(
        self,
        query: str,
        *,
        query_tag: Optional[str] = None,
    ):
        """
        Execute a read-only SQL query and return all rows.
        """

        if not query.strip().lower().startswith("select"):
            raise ValueError("Only SELECT queries are allowed")

        with self.connect(query_tag=query_tag) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()

        log_event(
            logger,
            "Databricks query executed",
            extra={
                "row_count": len(rows),
                "query_tag": query_tag,
            },
        )

        return columns, rows
