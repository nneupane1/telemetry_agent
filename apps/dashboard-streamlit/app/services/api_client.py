"""
Streamlit API Client.

Centralized HTTP client for communicating with the
GenAI Predictive Interpreter FastAPI backend.
"""

from __future__ import annotations

import os
import requests
from typing import Dict, Any, List

# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

API_BASE_URL = os.getenv(
    "API_BASE_URL",
    "http://localhost:8000",
)

TIMEOUT_SECONDS = 15


# ------------------------------------------------------------
# Low-level request helper
# ------------------------------------------------------------

def _request(
    method: str,
    path: str,
    json: Dict | None = None,
) -> Dict[str, Any]:
    """
    Internal HTTP request helper.
    """
    url = f"{API_BASE_URL}{path}"

    response = requests.request(
        method=method,
        url=url,
        json=json,
        timeout=TIMEOUT_SECONDS,
    )

    if not response.ok:
        raise RuntimeError(
            f"API request failed [{response.status_code}]: {response.text}"
        )

    return response.json()


# ------------------------------------------------------------
# Public API methods
# ------------------------------------------------------------

def fetch_vin_interpretation(vin: str) -> Dict[str, Any]:
    """
    Fetch VIN-level interpretation.
    """
    return _request("GET", f"/vin/{vin}")


def fetch_cohort_interpretation(cohort_id: str) -> Dict[str, Any]:
    """
    Fetch cohort-level interpretation.
    """
    return _request("GET", f"/cohort/{cohort_id}")


def fetch_chat_reply(
    message: str,
    context: Dict[str, Any] | None = None,
) -> str:
    """
    Request a GenAI chat explanation.
    """
    payload = {
        "message": message,
        "context": context,
    }

    result = _request("POST", "/chat", json=payload)
    return result["reply"]


def export_pdf(
    subject_type: str,
    subject_id: str,
) -> bytes:
    """
    Generate and return a PDF report.
    """
    url = f"{API_BASE_URL}/export/pdf"

    response = requests.post(
        url,
        json={
            "subject_type": subject_type,
            "subject_id": subject_id,
        },
        timeout=TIMEOUT_SECONDS,
    )

    if not response.ok:
        raise RuntimeError(
            f"PDF export failed [{response.status_code}]: {response.text}"
        )

    return response.content
