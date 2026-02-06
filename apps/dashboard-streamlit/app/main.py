"""
Operator Console (Streamlit).

Focused workflow:
1. Select VIN and fetch interpretation
2. Review evidence and recommendations
3. Create/export action pack
4. Capture approvals
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from app.services.api_client import (
    create_action_pack,
    export_pdf,
    fetch_chat_reply,
    fetch_cohort_list,
    fetch_cohort_interpretation,
    fetch_vin_interpretation,
    list_approvals,
    record_approval,
)


def _load_theme() -> None:
    css_path = Path(__file__).parent / "theme" / "streamlit_neon_theme.css"
    if css_path.exists():
        st.markdown(
            f"<style>{css_path.read_text(encoding='utf-8')}</style>",
            unsafe_allow_html=True,
        )


st.set_page_config(
    page_title="Telemetry Operator Console",
    page_icon="T",
    layout="wide",
)
_load_theme()

if "selected_vin" not in st.session_state:
    st.session_state.selected_vin = "WVWZZZ1KZ6W000001"
if "vin_data" not in st.session_state:
    st.session_state.vin_data = None
if "approval_actor" not in st.session_state:
    st.session_state.approval_actor = "control-room-operator"

st.title("Telemetry Operator Console")
st.caption("Databricks Unity Catalog telemetry interpreted by a multi-agent workflow.")

fleet_tab, evidence_tab, approval_tab, chat_tab = st.tabs(
    ["Fleet", "Evidence", "Approval", "Chat"]
)


@st.cache_data(ttl=60)
def _load_cohort_options() -> list[str]:
    try:
        rows = fetch_cohort_list()
    except Exception:
        return []

    options = []
    for row in rows:
        cohort_id = str(row.get("cohort_id", "")).strip()
        if cohort_id:
            options.append(cohort_id)

    return options

with fleet_tab:
    col1, col2 = st.columns([2, 1])
    with col1:
        vin = st.text_input(
            "VIN",
            value=st.session_state.selected_vin,
            help="Enter the VIN to inspect.",
        ).strip().upper()

        if st.button("Load VIN Interpretation", type="primary"):
            st.session_state.selected_vin = vin
            with st.spinner("Loading VIN interpretation..."):
                try:
                    st.session_state.vin_data = fetch_vin_interpretation(vin)
                    st.success(f"Loaded interpretation for {vin}")
                except Exception as exc:
                    st.error(f"VIN lookup failed: {exc}")

    with col2:
        cohort_options = _load_cohort_options()
        if not cohort_options:
            st.info("No cohorts available from /cohort/list.")
        else:
            cohort_id = st.selectbox(
                "Cohort",
                options=cohort_options,
            )
            if st.button("Load Cohort Snapshot"):
                with st.spinner("Loading cohort summary..."):
                    try:
                        cohort = fetch_cohort_interpretation(cohort_id)
                        st.metric(
                            "Anomaly Count",
                            len(cohort.get("anomalies", [])),
                        )
                        st.json(
                            {
                                "cohort_id": cohort.get("cohort_id"),
                                "summary": cohort.get("summary"),
                                "risk_distribution": cohort.get("risk_distribution"),
                            }
                        )
                    except Exception as exc:
                        st.error(f"Cohort lookup failed: {exc}")

    if st.session_state.vin_data:
        st.subheader("VIN Summary")
        st.write(st.session_state.vin_data.get("summary"))
        c1, c2, c3 = st.columns(3)
        c1.metric("Risk Level", st.session_state.vin_data.get("risk_level", "N/A"))
        c2.metric(
            "Recommendations",
            len(st.session_state.vin_data.get("recommendations", [])),
        )
        c3.metric(
            "Evidence Sources",
            len((st.session_state.vin_data.get("evidence_summary") or {}).keys()),
        )

with evidence_tab:
    st.subheader("Evidence Drilldown")
    vin_data = st.session_state.vin_data
    if not vin_data:
        st.info("Load a VIN in the Fleet tab first.")
    else:
        recommendations = vin_data.get("recommendations", [])
        if not recommendations:
            st.warning("No recommendation evidence available for this VIN.")
        for idx, rec in enumerate(recommendations, start=1):
            with st.expander(f"{idx}. {rec.get('title')} ({rec.get('urgency')})", expanded=(idx == 1)):
                st.write(rec.get("rationale"))
                evidence_rows = rec.get("evidence", [])
                if evidence_rows:
                    st.dataframe(evidence_rows, use_container_width=True)
                else:
                    st.caption("No evidence rows attached.")

with approval_tab:
    st.subheader("Action Pack and Approval")
    vin_data = st.session_state.vin_data
    if not vin_data:
        st.info("Load a VIN in the Fleet tab first.")
    else:
        default_payload = {
            "subject_type": "VIN",
            "subject_id": vin_data["vin"],
            "title": f"Action Pack for {vin_data['vin']}",
            "executive_summary": vin_data["summary"],
            "recommendations": vin_data.get("recommendations", []),
        }

        if st.button("Create Action Pack"):
            try:
                action_pack = create_action_pack(default_payload)
                st.success(f"Created {action_pack.get('action_pack_id')}")
                st.json(action_pack)
            except Exception as exc:
                st.error(f"Action pack creation failed: {exc}")

        if st.button("Export VIN PDF"):
            try:
                pdf_bytes = export_pdf("vin", vin_data["vin"])
                st.download_button(
                    "Download VIN Report PDF",
                    data=pdf_bytes,
                    file_name=f"vin-{vin_data['vin']}.pdf",
                    mime="application/pdf",
                )
            except Exception as exc:
                st.error(f"PDF export failed: {exc}")

        decision = st.radio(
            "Decision",
            options=["approve", "reject", "escalate"],
            horizontal=True,
        )
        comment = st.text_area(
            "Decision comment",
            placeholder="Explain the rationale for this decision.",
        )
        st.session_state.approval_actor = st.text_input(
            "Decided by",
            value=st.session_state.approval_actor,
        )

        if st.button("Record Approval", type="primary"):
            if not comment.strip():
                st.error("Comment is required.")
            else:
                try:
                    record = record_approval(
                        subject_type="vin",
                        subject_id=vin_data["vin"],
                        decision=decision,
                        comment=comment.strip(),
                        decided_by=st.session_state.approval_actor,
                    )
                    st.success("Approval decision recorded.")
                    st.json(record)
                except Exception as exc:
                    st.error(f"Approval write failed: {exc}")

        if st.button("Refresh Approval Log"):
            try:
                rows = list_approvals(
                    subject_type="vin",
                    subject_id=vin_data["vin"],
                )
                st.dataframe(rows, use_container_width=True)
            except Exception as exc:
                st.error(f"Unable to load approvals: {exc}")

with chat_tab:
    st.subheader("Explainability Chat")
    prompt = st.text_area(
        "Question",
        placeholder="Explain why this VIN is high risk.",
    )
    if st.button("Ask"):
        context = {}
        if st.session_state.vin_data:
            context = {
                "vin": st.session_state.vin_data["vin"],
                "risk_level": st.session_state.vin_data.get("risk_level"),
                "evidence_summary": st.session_state.vin_data.get("evidence_summary"),
            }
        try:
            reply = fetch_chat_reply(prompt, context=context)
            st.write(reply)
        except Exception as exc:
            st.error(f"Chat request failed: {exc}")
