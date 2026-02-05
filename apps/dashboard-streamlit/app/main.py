"""
GenAI Predictive Interpreter — Operator Dashboard

This Streamlit application is designed for control room operators
and service specialists to:
- inspect VIN-level evidence
- review GenAI interpretations
- approve or escalate recommended actions

This file defines the application shell and navigation.
"""

from __future__ import annotations

import streamlit as st

# ------------------------------------------------------------
# Page configuration (must be first Streamlit call)
# ------------------------------------------------------------

st.set_page_config(
    page_title="GenAI Operator Console",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------
# Global styling (dark / neon-lite)
# ------------------------------------------------------------

st.markdown(
    """
    <style>
        body {
            background-color: #05070D;
            color: #E6E9F2;
        }
        .stSidebar {
            background-color: #0A0F1F;
        }
        .neon-title {
            color: #9D7BFF;
            text-shadow: 0 0 12px rgba(157,123,255,0.4);
        }
        .muted {
            color: #AAB0D6;
        }
        .panel {
            background-color: #0E1428;
            border: 1px solid rgba(157,123,255,0.15);
            border-radius: 12px;
            padding: 1rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------
# Session state initialization
# ------------------------------------------------------------

if "selected_vin" not in st.session_state:
    st.session_state.selected_vin = None

if "approval_log" not in st.session_state:
    st.session_state.approval_log = []

# ------------------------------------------------------------
# Sidebar navigation
# ------------------------------------------------------------

st.sidebar.markdown(
    "<h2 class='neon-title'>Operator Console</h2>",
    unsafe_allow_html=True,
)

page = st.sidebar.radio(
    "Navigate",
    options=[
        "VIN Lookup",
        "Evidence Review",
        "Approval Queue",
    ],
)

st.sidebar.markdown(
    "<p class='muted'>GenAI-powered predictive maintenance</p>",
    unsafe_allow_html=True,
)

# ------------------------------------------------------------
# Page routing
# ------------------------------------------------------------

if page == "VIN Lookup":
    st.markdown("<h1 class='neon-title'>VIN Lookup</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p class='muted'>Search and inspect individual vehicle risk.</p>",
        unsafe_allow_html=True,
    )

    st.info("VIN lookup UI will be loaded here.")

elif page == "Evidence Review":
    st.markdown("<h1 class='neon-title'>Evidence Review</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p class='muted'>Inspect signals and supporting evidence.</p>",
        unsafe_allow_html=True,
    )

    st.info("Evidence viewer UI will be loaded here.")

elif page == "Approval Queue":
    st.markdown("<h1 class='neon-title'>Approval Queue</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p class='muted'>Approve, reject, or escalate Action Packs.</p>",
        unsafe_allow_html=True,
    )

    st.info("Approval workflow UI will be loaded here.")
