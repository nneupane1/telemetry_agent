"""
VIN Lookup Component.

Allows operators to search for and select a VIN,
persisting it into Streamlit session state.
"""

from __future__ import annotations

import re
import streamlit as st


VIN_REGEX = re.compile(r"^[A-HJ-NPR-Z0-9]{11,17}$")


def render_vin_lookup(
    title: str = "VIN Lookup",
    placeholder: str = "Enter VIN (e.g. WVWZZZ1KZ6W000001)",
) -> None:
    """
    Render a VIN lookup input.

    Args:
        title: Section title
        placeholder: Input placeholder text
    """

    st.markdown(
        f"<h2 class='neon-title'>{title}</h2>",
        unsafe_allow_html=True,
    )

    vin_input = st.text_input(
        "VIN",
        placeholder=placeholder,
    )

    if not vin_input:
        return

    vin = vin_input.strip().upper()

    # --------------------------------------------------
    # Lightweight validation
    # --------------------------------------------------

    if not VIN_REGEX.match(vin):
        st.error("Invalid VIN format.")
        return

    # --------------------------------------------------
    # Persist selection
    # --------------------------------------------------

    st.session_state.selected_vin = vin

    st.success(f"Selected VIN: {vin}")

    st.markdown(
        "<p class='muted'>You can now proceed to Evidence Review or Approval.</p>",
        unsafe_allow_html=True,
    )
