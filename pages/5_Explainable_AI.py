"""
pages/5_Explainable_AI.py

Explainable AI Lab — Feature importance + local sensitivity + correlation map.
Every chart is labelled with what its axes and scale mean.
"""
from __future__ import annotations

from src import bootstrap  # noqa: F401

import streamlit as st

from src.charts import correlation_heatmap, feature_importance_bar, local_impact_chart
from src.config import CORRELATION_FIELDS, PALETTE
from src.inference import (
    load_artifacts,
    load_reference_dataset,
    local_feature_impacts,
)
from src.insights import build_explanations
from src.session import ensure_baseline
from src.styles import (
    apply_styles,
    divider,
    hero,
    insight_chip,
    scale_note,
    score_legend,
    section_header,
)

st.set_page_config(page_title="Explainable AI Lab — Behavioral Intelligence Advisor", layout="wide")
apply_styles()

PLOTLY_CONFIG = {"responsive": True, "displayModeBar": "hover",
                 "modeBarButtonsToRemove": ["lasso2d", "select2d"]}

try:
    artifacts = load_artifacts()
    metadata  = artifacts["metadata"]
    reference = load_reference_dataset()
    analysis  = ensure_baseline(metadata, reference)
except Exception as exc:
    st.error(f"⚠️ Could not load models: {exc}. Please reload the Home page first.")
    st.stop()

# ── Hero ─────────────────────────────────────────────────────────────────────
st.markdown(
    hero(
        eyebrow="Page 06 — Explainability",
        title="Explainable AI Lab.",
        body=(
            "Open the black box. "
            "Global feature importance (Mean Decrease Impurity) shows which inputs drive the models overall. "
            "Local sensitivity analysis reveals which levers move YOUR specific prediction — "
            "by perturbing each feature and measuring the output change."
        ),
    ),
    unsafe_allow_html=True,
)

# ── Explainability guide ───────────────────────────────────────────────────────
with st.expander("ℹ️  How to read this page", expanded=False):
    st.markdown(
        """
**Two complementary explainability methods are used:**

| Method | Scope | How it works | Chart type |
|---|---|---|---|
| **Global Feature Importance** | Whole dataset · all users | RandomForest Mean Decrease Impurity (MDI) — measures how much each feature reduces prediction error across all decision trees | Horizontal bar · bars sum to 100% |
| **Local Sensitivity** | Your profile only | Each feature is nudged by a fixed amount; the change in predicted score is recorded | Diverging bar · red = raises risk · green = lowers it |

**Feature Importance scale:** Bars run 0% → 100%. A bar of 30% means that feature contributes ~30% of the model's total decision weight.

**Local Sensitivity scale:** Bars show the raw change in model output (stress, addiction severity, or productivity score).
- Positive (red) bar → nudging that feature UP increases the risk metric
- Negative (green) bar → nudging that feature UP decreases the risk metric (protective)

**Correlation heatmap scale:** Pearson r from –1.00 to +1.00.
- **+1.00** = perfect positive relationship
- **0.00** = no linear relationship
- **–1.00** = perfect inverse relationship
        """
    )

impacts      = local_feature_impacts(analysis["profile"])
explanations = build_explanations(impacts)

# ── Global feature importance ──────────────────────────────────────────────────
st.markdown(
    section_header(
        "Global Feature Importance",
        "RandomForest Mean Decrease Impurity across the full 16,000-record dataset. "
        "Shows which inputs matter most for each model overall — NOT specific to your profile.",
    ),
    unsafe_allow_html=True,
)
st.markdown(
    score_legend([
        ("Stress model",      PALETTE["primary"],   "Blue bars — regression model (predicts 0.00–1.00 continuous score)"),
        ("Addiction model",   PALETTE["accent"],    "Amber bars — 3-class classifier (Low / Moderate / High)"),
        ("Productivity model", PALETTE["secondary"], "Green bars — binary classifier (Stable / Impacted)"),
    ]),
    unsafe_allow_html=True,
)
st.markdown(
    scale_note(
        "X-axis: Share of model decision weight (0–100%). All bars in each chart sum to 100%. "
        "A longer bar means that feature plays a larger role in the model's predictions."
    ),
    unsafe_allow_html=True,
)

imp_cols = st.columns(3)
with imp_cols[0]:
    st.plotly_chart(
        feature_importance_bar(metadata["feature_importance"]["stress"], "stress"),
        width="stretch", config=PLOTLY_CONFIG,
    )
with imp_cols[1]:
    st.plotly_chart(
        feature_importance_bar(metadata["feature_importance"]["addiction"], "addiction"),
        width="stretch", config=PLOTLY_CONFIG,
    )
with imp_cols[2]:
    st.plotly_chart(
        feature_importance_bar(metadata["feature_importance"]["productivity"], "productivity"),
        width="stretch", config=PLOTLY_CONFIG,
    )

# ── Local sensitivity ──────────────────────────────────────────────────────────
st.markdown(
    section_header(
        "Local Sensitivity — Your Profile",
        "How your specific predictions respond to a ±1 unit change in each lifestyle feature. "
        "This is a profile-specific view — your results will differ from the global importance above.",
    ),
    unsafe_allow_html=True,
)
st.markdown(
    score_legend([
        ("Increases risk",  PALETTE["danger"],    "Red bar — raising this feature RAISES the risk metric"),
        ("Reduces risk",    PALETTE["secondary"], "Green bar — raising this feature LOWERS the risk metric (protective)"),
    ]),
    unsafe_allow_html=True,
)
st.markdown(
    scale_note(
        "X-axis: Predicted change in model output score (e.g. +0.04 means stress increases by 0.04 on a 0–1 scale). "
        "Each feature is nudged by a fixed positive delta (Screen Time +1h, Sleep +0.5h, etc.)."
    ),
    unsafe_allow_html=True,
)
st.caption(
    "Perturbation-based local sensitivity — each feature nudged by a fixed delta; "
    "output change recorded. Not full SHAP, but directionally consistent."
)

local_cols = st.columns(3)
with local_cols[0]:
    st.plotly_chart(local_impact_chart(impacts, "stress"),      width="stretch", config=PLOTLY_CONFIG)
with local_cols[1]:
    st.plotly_chart(local_impact_chart(impacts, "addiction"),   width="stretch", config=PLOTLY_CONFIG)
with local_cols[2]:
    st.plotly_chart(local_impact_chart(impacts, "productivity"), width="stretch", config=PLOTLY_CONFIG)

# ── Causal explanation cards ───────────────────────────────────────────────────
st.markdown(divider("Auto-Generated Explanations"), unsafe_allow_html=True)
st.caption(
    "Text summaries of the two features most influential to your local sensitivity scores. "
    "Direction (raising / reducing) refers to the effect of increasing that feature."
)
exp_cols = st.columns(3)
exp_cols[0].markdown(
    insight_chip(f"<strong>🔵 Stress.</strong> {explanations['stress']}"),
    unsafe_allow_html=True,
)
exp_cols[1].markdown(
    insight_chip(f"<strong>🟡 Addiction.</strong> {explanations['addiction']}", tone="warning"),
    unsafe_allow_html=True,
)
exp_cols[2].markdown(
    insight_chip(f"<strong>🟢 Productivity.</strong> {explanations['productivity']}"),
    unsafe_allow_html=True,
)

# ── Correlation heatmap ────────────────────────────────────────────────────────
st.markdown(
    section_header(
        "Behavioral Correlation Map",
        "Pearson correlation between all key behavioral and outcome variables across the full 16,000-record dataset. "
        "This shows natural co-occurrence patterns — NOT model predictions.",
    ),
    unsafe_allow_html=True,
)
st.markdown(
    score_legend([
        ("+1.00 (blue)",  PALETTE["primary"], "Strong positive link (both go up together)"),
        ("0.00 (white)", "#E5E7EB",           "No linear relationship"),
        ("−1.00 (amber)", PALETTE["accent"],  "Strong inverse link (one goes up, other goes down)"),
    ]),
    unsafe_allow_html=True,
)
st.markdown(
    scale_note(
        "Diagonal = always 1.00 (a variable perfectly correlates with itself). "
        "Correlations ≥ |0.3| are worth examining. Correlations ≥ |0.6| indicate strong relationships. "
        "Hover any cell to see the exact Pearson r value."
    ),
    unsafe_allow_html=True,
)
st.plotly_chart(
    correlation_heatmap(reference, CORRELATION_FIELDS),
    width="stretch", config=PLOTLY_CONFIG,
)
st.markdown(
    insight_chip(
        "<strong>Note on causality.</strong> Correlation does not imply causation. "
        "A strong correlation between screen time and stress does not mean screen time causes stress — "
        "both could be driven by a common factor such as work pressure or deadline cycles.",
        tone="info",
    ),
    unsafe_allow_html=True,
)
