"""
Evidence Review Page.

Displays predictive signals and confidence levels
supporting GenAI interpretations for a selected VIN.
"""

from __future__ import annotations

import streamlit as st

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
# Placeholder evidence data (API wiring later)
# ------------------------------------------------------------

evidence = [
    {
        "source": "Machine Health",
        "signal_code": "HI-4302",
        "description": "Fuel pressure instability detected",
        "confidence": 0.91,
    },
    {
        "source": "Maintenance Prediction",
        "signal_code": "MP-1107",
        "description": "Elevated maintenance probability",
        "confidence": 0.78,
    },
    {
        "source": "Failure Impact Model",
        "signal_code": "FIM-22",
        "description": "Fuel pump failure impact elevated",
        "confidence": 0.83,
    },
]

# ------------------------------------------------------------
# Evidence rendering
# ------------------------------------------------------------

for ev in evidence:
    st.markdown("<div class='panel'>", unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown(
            f"""
            <strong>{ev['signal_code']}</strong> — {ev['description']}  
            <br/><span class='muted'>Source: {ev['source']}</span>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.metric(
            "Confidence",
            f"{int(ev['confidence'] * 100)}%",
        )

    st.markdown("</div>", unsafe_allow_html=True)
