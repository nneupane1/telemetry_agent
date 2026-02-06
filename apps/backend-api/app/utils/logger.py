"""
Centralized logging configuration for the GenAI Predictive Interpreter Platform.

Design goals:
- Structured JSON logs (machine + human readable)
- Correlation / trace IDs for forensic reconstruction
- Safe for GenAI systems (no prompt / secret leakage)
- Compatible with ELK, Datadog, Splunk, CloudWatch
- Zero global state mutation beyond logging
"""

from __future__ import annotations

import logging
import os
import sys
import uuid
from contextvars import ContextVar
from datetime import datetime
from typing import Any, Dict, Optional

from app.utils.config import load_config

# ---------------------------------------------------------------------
# Context variables (request / trace scoped)
# ---------------------------------------------------------------------

request_id_ctx: ContextVar[Optional[str]] = ContextVar("request_id", default=None)
vin_ctx: ContextVar[Optional[str]] = ContextVar("vin", default=None)
agent_ctx: ContextVar[Optional[str]] = ContextVar("agent", default=None)


# ---------------------------------------------------------------------
# Helpers to set / get context
# ---------------------------------------------------------------------

def set_request_id(request_id: Optional[str] = None) -> str:
    rid = request_id or str(uuid.uuid4())
    request_id_ctx.set(rid)
    return rid


def set_vin(vin: Optional[str]) -> None:
    vin_ctx.set(vin)


def set_agent(agent_name: Optional[str]) -> None:
    agent_ctx.set(agent_name)


def _get_context() -> Dict[str, Optional[str]]:
    return {
        "request_id": request_id_ctx.get(),
        "vin": vin_ctx.get(),
        "agent": agent_ctx.get(),
    }


# ---------------------------------------------------------------------
# JSON Log Formatter
# ---------------------------------------------------------------------

class JsonLogFormatter(logging.Formatter):
    """
    Structured JSON formatter with forensic metadata.
    """

    def format(self, record: logging.LogRecord) -> str:
        base: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(timespec="milliseconds") + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Attach forensic context
        base.update({k: v for k, v in _get_context().items() if v})

        # Exception info (clean, stack preserved)
        if record.exc_info:
            base["exception"] = self.formatException(record.exc_info)

        # Extra structured fields (safe only)
        if hasattr(record, "extra_fields"):
            base.update(record.extra_fields)

        return _to_json(base)


def _to_json(payload: Dict[str, Any]) -> str:
    try:
        import json
        return json.dumps(payload, default=str)
    except Exception:
        # Absolute last-resort fallback
        return str(payload)


# ---------------------------------------------------------------------
# Logger Factory
# ---------------------------------------------------------------------

def get_logger(name: str) -> logging.Logger:
    """
    Create or retrieve a configured logger.
    """

    logger = logging.getLogger(name)

    if logger.handlers:
        return logger  # already configured

    # Keep logger usable even when full app config is unavailable
    # (e.g., unit tests without Databricks/OpenAI env vars).
    try:
        log_level = load_config().log_level.upper()
    except Exception:
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    logger.setLevel(log_level)
    logger.propagate = False

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonLogFormatter())

    logger.addHandler(handler)

    return logger


# ---------------------------------------------------------------------
# Safe logging helpers (GenAI-aware)
# ---------------------------------------------------------------------

def log_event(
    logger: logging.Logger,
    message: str,
    *,
    level: int = logging.INFO,
    extra: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Log a structured event with safe extra fields.

    Never log:
    - raw prompts
    - secrets
    - tokens
    - credentials
    """

    safe_extra = _sanitize(extra or {})

    logger.log(
        level,
        message,
        extra={"extra_fields": safe_extra},
    )


def _sanitize(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Best-effort sanitization to prevent sensitive leakage.
    """
    blocked_keys = {
        "api_key",
        "token",
        "password",
        "secret",
        "authorization",
        "prompt",
        "raw_prompt",
    }

    sanitized: Dict[str, Any] = {}
    for k, v in data.items():
        if k.lower() in blocked_keys:
            sanitized[k] = "***REDACTED***"
        else:
            sanitized[k] = v
    return sanitized
