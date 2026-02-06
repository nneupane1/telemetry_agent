"""
Approval page for Streamlit multipage mode.
"""

from __future__ import annotations

import streamlit as st

from app.services.api_client import (
    create_action_pack,
    fetch_vin_interpretation,
    list_approvals,
    record_approval,
)

st.title("Approval Queue")

vin = st.session_state.get("selected_vin")
if not vin:
    st.warning("No VIN selected. Use the main Fleet tab or Dashboard page first.")
    st.stop()

st.caption(f"VIN: {vin}")

try:
    interpretation = fetch_vin_interpretation(vin)
except Exception as exc:
    st.error(f"Failed to load VIN interpretation: {exc}")
    st.stop()

st.subheader("Proposed Action Pack")
st.write(interpretation.get("summary"))

if st.button("Create Action Pack"):
    payload = {
        "subject_type": "VIN",
        "subject_id": vin,
        "title": f"Action Pack for {vin}",
        "executive_summary": interpretation.get("summary", ""),
        "recommendations": interpretation.get("recommendations", []),
    }
    try:
        action_pack = create_action_pack(payload)
        st.success(f"Created {action_pack.get('action_pack_id')}")
        st.json(action_pack)
    except Exception as exc:
        st.error(f"Action pack creation failed: {exc}")

decision = st.radio("Decision", ["approve", "reject", "escalate"], horizontal=True)
comment = st.text_area("Comment", placeholder="Provide rationale for this decision.")
actor = st.text_input("Decided by", value="control-room-operator")

if st.button("Record Decision", type="primary"):
    if not comment.strip():
        st.error("Comment is required.")
    else:
        try:
            record = record_approval(
                subject_type="vin",
                subject_id=vin,
                decision=decision,
                comment=comment.strip(),
                decided_by=actor,
            )
            st.success("Decision recorded.")
            st.json(record)
        except Exception as exc:
            st.error(f"Approval write failed: {exc}")

if st.button("Refresh Approval History"):
    try:
        rows = list_approvals(subject_type="vin", subject_id=vin)
        st.dataframe(rows, use_container_width=True)
    except Exception as exc:
        st.error(f"Failed to load approval history: {exc}")

