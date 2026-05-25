from __future__ import annotations

import pandas as pd
import streamlit as st

from src.inference import analyze_profile


def ensure_baseline(metadata: dict[str, object], reference: pd.DataFrame) -> dict[str, object]:
    """Make subpages safe even when opened directly without visiting Home first."""
    if "baseline_inputs" not in st.session_state:
        st.session_state.baseline_inputs = dict(metadata["defaults"])
    if "analysis" not in st.session_state:
        st.session_state.analysis = analyze_profile(
            st.session_state.baseline_inputs, reference
        )
    return st.session_state.analysis
