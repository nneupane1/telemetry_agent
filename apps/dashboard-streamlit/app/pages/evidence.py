"""
Evidence Review Page.

Fetches and displays real predictive evidence for the
currently selected VIN using the backend API.
"""

from __future__ import annotations

import streamlit as st

from app.services.api_client import fetch_vin_interpretation
from app.components.EvidenceViewer import render_evidence_viewer


# ------------------------------------------------------------
# Page header
# ------------------------------------------------------------

st.markdown(
    "<h1 class='neon-title'>Evidence Review</h1>",
    unsafe_allow_html=True,
)

st.markdown(
    "<p class='muted'>Inspect predictive signals and confidence levels.</p>",
    unsafe_allow_html=True,
)

# ------------------------------------------------------------
# VIN context
# ------------------------------------------------------------

vin = st.session_state.get("selected_vin")

if not vin:
    st.warning("No VIN selected. Please select a VIN from the Dashboard.")
    st.stop()

st.markdown(
    f"<p class='muted'>VIN: <strong>{vin}</strong></p>",
    unsafe_allow_html=True,
)

# ------------------------------------------------------------
# Fetch interpretation
# ------------------------------------------------------------

with st.spinner("Loading evidence…"):
    try:
        interpretation = fetch_vin_interpretation(vin)
    except Exception as exc:
        st.error(f"Failed to load evidence: {exc}")
        st.stop()

# ------------------------------------------------------------
# Extract evidence safely
# ------------------------------------------------------------

evidence = []
for rec in interpretation.get("recommendations", []):
    for ev in rec.get("evidence", []):
        evidence.append({
            "source_model": ev.get("source_model", "Unknown"),
            "signal_code": ev.get("signal_code"),
            "description": ev.get("signal_description"),
            "confidence": ev.get("confidence", 0.0),
            "observed_at": ev.get("observed_at"),
        })

# ------------------------------------------------------------
# Render evidence
# ------------------------------------------------------------

render_evidence_viewer(
    evidence=evidence,
    title="Predictive Evidence",
)
