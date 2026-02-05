"""
Operator Dashboard Page.

Live fleet snapshot with VIN lookup and cohort triage,
wired to the FastAPI backend.
"""

from __future__ import annotations

import streamlit as st

from app.services.api_client import (
    fetch_vin_interpretation,
    fetch_cohort_interpretation,
)
from app.components.VinLookup import render_vin_lookup
from app.components.CohortExplorer import render_cohort_explorer


# ------------------------------------------------------------
# Page header
# ------------------------------------------------------------

st.markdown(
    "<h1 class='neon-title'>Fleet Snapshot</h1>",
    unsafe_allow_html=True,
)

st.markdown(
    "<p class='muted'>Live operational overview of fleet risk.</p>",
    unsafe_allow_html=True,
)

# ------------------------------------------------------------
# VIN Lookup (left → right operator flow)
# ------------------------------------------------------------

render_vin_lookup()

st.divider()

# ------------------------------------------------------------
# Cohort Snapshot (example cohorts, live-backed)
# ------------------------------------------------------------

# NOTE:
# In real deployments, this list typically comes from:
# - a predefined cohort registry
# - or a backend endpoint (/cohort/list)
#
# For now, we demonstrate with known cohort IDs.

cohort_ids = [
    "EURO6-DIESEL",
    "EURO5-DIESEL",
    "EV-FLEET",
]

cohorts = []

with st.spinner("Loading cohort snapshot…"):
    for cid in cohort_ids:
        try:
            data = fetch_cohort_interpretation(cid)

            cohorts.append({
                "cohort_id": cid,
                "description": f"Fleet cohort: {cid}",
                "risk_level": (
                    "HIGH"
                    if data.get("anomalies")
                    else "LOW"
                ),
                "affected_vins": sum(
                    a.get("affected_vin_count", 0)
                    for a in data.get("anomalies", [])
                ),
            })

        except Exception:
            # Fail-soft: skip unavailable cohorts
            continue

# ------------------------------------------------------------
# Render Cohort Explorer
# ------------------------------------------------------------

render_cohort_explorer(
    cohorts=cohorts,
    title="Cohort Risk Overview",
)

# ------------------------------------------------------------
# Operator guidance
# ------------------------------------------------------------

st.markdown(
    """
    <p class='muted'>
    Tip: Start with a cohort to identify risk concentration,
    then drill down into individual VINs for evidence and approval.
    </p>
    """,
    unsafe_allow_html=True,
)
