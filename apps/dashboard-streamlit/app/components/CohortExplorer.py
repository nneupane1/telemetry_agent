"""
Cohort Explorer Component.

Provides a fast, readable interface for operators to
inspect and select fleet cohorts for deeper analysis.
"""

from __future__ import annotations

import streamlit as st
from typing import List, Dict


def render_cohort_explorer(
    cohorts: List[Dict],
    title: str = "Cohort Explorer",
) -> None:
    """
    Render a cohort explorer list.

    Args:
        cohorts: List of cohort dictionaries with keys:
            - cohort_id
            - description
            - risk_level
            - affected_vins
        title: Section title
    """

    st.markdown(
        f"<h2 class='neon-title'>{title}</h2>",
        unsafe_allow_html=True,
    )

    if not cohorts:
        st.info("No cohorts available.")
        return

    for cohort in cohorts:
        risk = cohort.get("risk_level", "UNKNOWN")
        cohort_id = cohort.get("cohort_id")

        # Risk color (minimal, operator-safe)
        if risk == "HIGH":
            risk_color = "#FF4F4F"
        elif risk == "ELEVATED":
            risk_color = "#FFB020"
        else:
            risk_color = "#2BFF88"

        st.markdown("<div class='panel'>", unsafe_allow_html=True)

        col1, col2 = st.columns([4, 1])

        with col1:
            st.markdown(
                f"""
                <strong>{cohort_id}</strong><br/>
                <span class='muted'>{cohort.get("description", "")}</span><br/>
                <span style="color:{risk_color}">
                    Risk: {risk}
                </span>
                """,
                unsafe_allow_html=True,
            )

        with col2:
            st.metric(
                "VINs",
                cohort.get("affected_vins", 0),
            )

            if st.button(
                "Select",
                key=f"select_{cohort_id}",
            ):
                st.session_state.selected_cohort = cohort_id
                st.success(f"Selected cohort: {cohort_id}")

        st.markdown("</div>", unsafe_allow_html=True)
