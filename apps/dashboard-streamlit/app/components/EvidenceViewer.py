"""
Evidence Viewer Component.

Displays predictive evidence (MH / MP / FIM) with
clear provenance and confidence for operator review.
"""

from __future__ import annotations

from typing import List, Dict
import streamlit as st


def render_evidence_viewer(
    evidence: List[Dict],
    title: str = "Predictive Evidence",
) -> None:
    """
    Render predictive evidence grouped by source model.

    Args:
        evidence: List of evidence dictionaries with keys:
            - source_model (e.g. Machine Health, MP, FIM)
            - signal_code
            - description
            - confidence (0–1)
            - observed_at (optional)
        title: Section title
    """

    st.markdown(
        f"<h2 class='neon-title'>{title}</h2>",
        unsafe_allow_html=True,
    )

    if not evidence:
        st.info("No evidence available.")
        return

    # --------------------------------------------------
    # Group evidence by source model
    # --------------------------------------------------

    grouped: Dict[str, List[Dict]] = {}
    for ev in evidence:
        grouped.setdefault(ev.get("source_model", "Unknown"), []).append(ev)

    # --------------------------------------------------
    # Render groups
    # --------------------------------------------------

    for source, items in grouped.items():
        st.markdown(
            f"<h3 class='muted'>{source}</h3>",
            unsafe_allow_html=True,
        )

        for ev in items:
            confidence_pct = int(ev.get("confidence", 0) * 100)

            # Confidence color (operator-safe)
            if confidence_pct >= 80:
                conf_color = "#2BFF88"
            elif confidence_pct >= 60:
                conf_color = "#FFB020"
            else:
                conf_color = "#FF4F4F"

            st.markdown("<div class='panel'>", unsafe_allow_html=True)

            col1, col2 = st.columns([4, 1])

            with col1:
                st.markdown(
                    f"""
                    <strong>{ev.get("signal_code")}</strong><br/>
                    {ev.get("description")}<br/>
                    <span class='muted'>
                        Observed: {ev.get("observed_at", "N/A")}
                    </span>
                    """,
                    unsafe_allow_html=True,
                )

            with col2:
                st.markdown(
                    f"""
                    <span style="color:{conf_color}; font-weight:600">
                        {confidence_pct}%
                    </span>
                    """,
                    unsafe_allow_html=True,
                )

            st.markdown("</div>", unsafe_allow_html=True)
