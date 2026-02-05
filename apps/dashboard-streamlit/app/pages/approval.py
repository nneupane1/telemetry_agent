"""
Approval Page.

Allows operators to approve, reject, or escalate
Action Packs with auditable decision logging.
"""

from __future__ import annotations

from datetime import datetime
import streamlit as st

# ------------------------------------------------------------
# Page header
# ------------------------------------------------------------

st.markdown(
    "<h1 class='neon-title'>Approval Queue</h1>",
    unsafe_allow_html=True,
)

st.markdown(
    "<p class='muted'>Review and decide on recommended actions.</p>",
    unsafe_allow_html=True,
)

# ------------------------------------------------------------
# VIN context
# ------------------------------------------------------------

vin = st.session_state.get("selected_vin")

if not vin:
    st.warning("No VIN selected. Please select a VIN first.")
    st.stop()

st.markdown(
    f"<p class='muted'>VIN: <strong>{vin}</strong></p>",
    unsafe_allow_html=True,
)

# ------------------------------------------------------------
# Placeholder Action Pack summary (API wiring later)
# ------------------------------------------------------------

st.markdown("<div class='panel'>", unsafe_allow_html=True)
st.markdown(
    """
    <strong>Proposed Action</strong><br/>
    Inspect fuel pressure system and related components within the next service window.
    """,
    unsafe_allow_html=True,
)
st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------------------------
# Decision input
# ------------------------------------------------------------

decision = st.radio(
    "Decision",
    options=["Approve", "Reject", "Escalate"],
    horizontal=True,
)

comment = st.text_area(
    "Comment (required)",
    placeholder="Provide rationale for this decision...",
)

# ------------------------------------------------------------
# Submit decision
# ------------------------------------------------------------

if st.button("Submit Decision", type="primary"):
    if not comment.strip():
        st.error("Comment is required for audit purposes.")
    else:
        entry = {
            "vin": vin,
            "decision": decision,
            "comment": comment.strip(),
            "timestamp": datetime.utcnow().isoformat(),
        }

        st.session_state.approval_log.append(entry)

        st.success(f"Decision '{decision}' recorded for VIN {vin}.")

        # Optional: clear comment box
        st.session_state.selected_vin = vin
