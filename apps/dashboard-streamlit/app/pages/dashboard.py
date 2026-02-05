"""
Operator Dashboard Page.

Provides a fleet snapshot and fast VIN lookup
for control room operators.
"""

from __future__ import annotations

import streamlit as st

# ------------------------------------------------------------
# Page header
# ------------------------------------------------------------

st.markdown(
    "<h1 class='neon-title'>Fleet Snapshot</h1>",
    unsafe_allow_html=True,
)

st.markdown(
    "<p class='muted'>Quick overview of fleet risk and VIN access.</p>",
    unsafe_allow_html=True,
)

# ------------------------------------------------------------
# Fleet KPIs (placeholder demo values)
# ------------------------------------------------------------

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.metric("Fleet HI", "64", delta="-3")
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.metric("High Risk VINs", "27")
    st.markdown("</div>", unsafe_allow_html=True)

with col3:
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.metric("Elevated Risk VINs", "92")
    st.markdown("</div>", unsafe_allow_html=True)

with col4:
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.metric("Active Action Packs", "18")
    st.markdown("</div>", unsafe_allow_html=True)

st.divider()

# ------------------------------------------------------------
# VIN Lookup
# ------------------------------------------------------------

st.markdown(
    "<h2 class='neon-title'>VIN Lookup</h2>",
    unsafe_allow_html=True,
)

vin_input = st.text_input(
    "Enter VIN",
    placeholder="e.g. WVWZZZ1KZ6W000001",
)

if vin_input:
    st.session_state.selected_vin = vin_input.strip().upper()
    st.success(f"Selected VIN: {st.session_state.selected_vin}")

    st.markdown(
        "<p class='muted'>Navigate to Evidence Review to inspect signals.</p>",
        unsafe_allow_html=True,
    )
