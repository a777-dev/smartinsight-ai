"""
pages/3_AI_Risk_Prediction.py

AI Risk Prediction — Three RandomForest models evaluated on a held-out test set.
Each metric card now includes a scale legend so readers understand what the number means.
"""
from __future__ import annotations

from src import bootstrap  # noqa: F401

import streamlit as st

from src.charts import gauge
from src.config import PALETTE
from src.inference import load_artifacts, load_reference_dataset
from src.session import ensure_baseline
from src.styles import (
    apply_styles,
    divider,
    hero,
    insight_chip,
    metric_card,
    scale_note,
    score_legend,
    section_header,
)

st.set_page_config(page_title="AI Risk Prediction — Behavioral Intelligence Advisor", layout="wide")
apply_styles()

PLOTLY_CONFIG = {"responsive": True, "displayModeBar": "hover",
                 "modeBarButtonsToRemove": ["lasso2d", "select2d", "autoScale2d"]}

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
        eyebrow="Page 04 — Machine Learning",
        title="AI Risk Prediction.",
        body=(
            "Three RandomForest models predict your stress level, addiction category, "
            "and productivity risk from raw behavioural inputs — no derived scores in the feature set. "
            "All evaluation metrics are reported on a stratified 20% held-out test set (not training data)."
        ),
    ),
    unsafe_allow_html=True,
)

# ── How to read this page ─────────────────────────────────────────────────────
with st.expander("ℹ️  How to read this page", expanded=False):
    st.markdown(
        """
**Three models, three tasks:**
| Model | Task type | Output | Key metric |
|---|---|---|---|
| Stress | **Regression** | Continuous score 0.00–1.00 | RMSE (lower = better) |
| Addiction | **3-class classification** | Low / Moderate / High | Accuracy + F1 (weighted) |
| Productivity | **Binary classification** | Impacted / Stable | Accuracy + F1 (weighted) |

**Reading the gauges:** All gauges run 0.00 → 1.00.
- 🟢 0.00–0.33 = low risk zone
- 🟡 0.33–0.66 = moderate zone
- 🔴 0.66–1.00 = high risk zone

**What RMSE means:** Root Mean Squared Error for the stress regressor.
An RMSE of 0.08 means the model's prediction is typically within ±0.08 of the true normalised stress score (range 0–1).

**What F1 (weighted) means:** Harmonic mean of precision and recall,
weighted by class frequency. Range 0.00–1.00. A score of 0.85+ is strong for a 3-class imbalanced problem.
        """
    )

# ── Model evaluation metrics ──────────────────────────────────────────────────
st.markdown(
    section_header(
        "Model Evaluation Metrics",
        "Computed once on a held-out test set (20% of 16,000 records, stratified by addiction category). "
        "These numbers do NOT come from training data.",
    ),
    unsafe_allow_html=True,
)
st.markdown(
    score_legend([
        ("Stress RMSE", PALETTE["primary"],    "Lower is better · 0.00 = perfect · typical strong range < 0.12"),
        ("Accuracy",    PALETTE["secondary"],  "Higher is better · 1.00 = perfect · weighted for class balance"),
        ("F1 (weighted)", PALETTE["accent"],   "Higher is better · 0.00–1.00 · accounts for class imbalance"),
    ]),
    unsafe_allow_html=True,
)

metrics = metadata["metrics"]
row1 = st.columns(3)

row1[0].markdown(
    metric_card(
        "Stress RMSE",
        f"{metrics['stress_rmse']:.3f}",
        delta="Regression model · lower = more accurate",
        accent="primary",
        scale="Scale 0.00–1.00 · ±0.05 difference on normalised stress score",
    ),
    unsafe_allow_html=True,
)
row1[1].markdown(
    metric_card(
        "Addiction Accuracy",
        f"{metrics['addiction_accuracy'] * 100:.1f}%",
        delta=f"Weighted F1 = {metrics['addiction_f1']:.3f}",
        accent="warning",
        scale="3-class (Low / Moderate / High) · balanced_subsample class weights",
    ),
    unsafe_allow_html=True,
)
row1[2].markdown(
    metric_card(
        "Productivity Accuracy",
        f"{metrics['productivity_accuracy'] * 100:.1f}%",
        delta=f"Weighted F1 = {metrics['productivity_f1']:.3f}",
        accent="secondary",
        scale="Binary (Impacted / Stable) · balanced_subsample class weights",
    ),
    unsafe_allow_html=True,
)

row2 = st.columns(3)
row2[0].markdown(
    metric_card(
        "Training Records",
        f"{int(metadata['dataset_summary']['rows'] * 0.8):,}",
        delta="80% of 16,000-record unified dataset",
        accent="accent",
        scale="Remaining 20% (~3,200) held out for evaluation above",
    ),
    unsafe_allow_html=True,
)
row2[1].markdown(
    metric_card(
        "Test Records",
        f"{int(metadata['dataset_summary']['rows'] * 0.2):,}",
        delta="Stratified split preserves class distribution",
        accent="primary",
        scale="Stratified by Addiction_Category to preserve Low/Mod/High ratios",
    ),
    unsafe_allow_html=True,
)
row2[2].markdown(
    metric_card(
        "Algorithm",
        "RandomForest",
        delta="250–300 trees · max_depth 12–14 · random_state 42",
        accent="primary",
        scale="Ensemble of decision trees · balanced_subsample for imbalanced classes",
    ),
    unsafe_allow_html=True,
)

# ── Live prediction gauges ─────────────────────────────────────────────────────
st.markdown(
    section_header(
        "Live Prediction for Your Profile",
        "Set your profile on the Home page · sliders update all predictions here automatically.",
    ),
    unsafe_allow_html=True,
)
st.markdown(
    score_legend([
        ("Low (safe)",      "#10B981", "0.00 – 0.33"),
        ("Moderate (watch)", "#F59E0B", "0.34 – 0.66"),
        ("High (risk)",     "#EF4444", "0.67 – 1.00"),
    ]),
    unsafe_allow_html=True,
)
st.markdown(
    scale_note(
        "All gauges run 0.00 to 1.00 · "
        "Stress = normalised stress intensity · "
        "Addiction Severity = weighted probability of High class · "
        "Productivity Outlook = probability of NOT being impacted (inverted risk)"
    ),
    unsafe_allow_html=True,
)

gauge_cols = st.columns(3)
gauge_cols[0].plotly_chart(
    gauge(
        "Predicted Stress Level",
        analysis["stress_level"],
        0.0, 1.0,
        PALETTE["danger"] if analysis["stress_level"] >= 0.55 else PALETTE["primary"],
        scale_label="0.00 = lowest stress  ·  1.00 = extreme stress",
    ),
    width="stretch", config=PLOTLY_CONFIG,
)
gauge_cols[1].plotly_chart(
    gauge(
        "Addiction Severity",
        analysis["addiction"]["severity"],
        0.0, 1.0,
        PALETTE["accent"],
        scale_label="0.00 = no dependency signals  ·  1.00 = strong dependency signals",
    ),
    width="stretch", config=PLOTLY_CONFIG,
)
gauge_cols[2].plotly_chart(
    gauge(
        "Productivity Outlook",
        analysis["productivity"]["productivity_score"],
        0.0, 1.0,
        PALETTE["secondary"],
        scale_label="0.00 = highly impacted  ·  1.00 = fully stable / productive",
    ),
    width="stretch", config=PLOTLY_CONFIG,
)

# ── Class probabilities ────────────────────────────────────────────────────────
st.markdown(divider("Class Probabilities"), unsafe_allow_html=True)
st.markdown(
    scale_note(
        "Probabilities are the model's confidence in each class. They sum to 100%. "
        "Addiction uses 3 classes (Low / Moderate / High). "
        "Productivity uses 2 classes (Stable / Impacted)."
    ),
    unsafe_allow_html=True,
)

prob_cols = st.columns(2)

with prob_cols[0]:
    st.markdown("**Addiction Category — Class Probabilities**")
    st.caption("Three-class classifier · probabilities sum to 100% · your predicted class is the highest bar")
    for label, prob in sorted(
        analysis["addiction"]["probabilities"].items(),
        key=lambda x: ["Low", "Moderate", "High"].index(x[0]),
    ):
        tone = "danger" if label == "High" else "warning" if label == "Moderate" else "default"
        bar_width = int(prob * 100)
        st.markdown(
            insight_chip(
                f"<strong>{label}</strong> — {prob * 100:.1f}% confidence"
                f"<div style='margin-top:6px;height:6px;background:var(--border);'>"
                f"<div style='width:{bar_width}%;height:100%;background:"
                f"{'var(--danger)' if label=='High' else 'var(--accent)' if label=='Moderate' else 'var(--secondary)'}'></div>"
                f"</div>",
                tone=tone,
            ),
            unsafe_allow_html=True,
        )

with prob_cols[1]:
    st.markdown("**Productivity Impact — Class Probabilities**")
    st.caption("Binary classifier · probability of each outcome for your profile")
    impact_pct = analysis["productivity"]["impact_probability"] * 100
    stable_pct  = analysis["productivity"]["productivity_score"] * 100
    for label, pct, tone in [
        ("Productivity Impacted", impact_pct, "danger" if impact_pct > 50 else "warning"),
        ("Productivity Stable",   stable_pct,  "default"),
    ]:
        bar_width = int(pct)
        st.markdown(
            insight_chip(
                f"<strong>{label}</strong> — {pct:.1f}% probability"
                f"<div style='margin-top:6px;height:6px;background:var(--border);'>"
                f"<div style='width:{bar_width}%;height:100%;background:"
                f"{'var(--danger)' if tone=='danger' else 'var(--secondary)'}'></div>"
                f"</div>",
                tone=tone,
            ),
            unsafe_allow_html=True,
        )
    st.markdown(
        insight_chip(
            f"<strong>Behavioral Risk Index.</strong> {analysis['behavioral_risk_index']:.3f} / 1.00"
            f" — composite score from screen time, stress, sleep, social media.",
            tone="info",
        ),
        unsafe_allow_html=True,
    )

# ── Model methodology note ─────────────────────────────────────────────────────
st.markdown(divider("Methodology"), unsafe_allow_html=True)
st.markdown(
    insight_chip(
        "<strong>Feature set.</strong> 9 raw numeric inputs + 4 categorical inputs. "
        "No derived scores (BRI, Addiction_Level_Norm) are used as features — "
        "preventing data leakage from engineered targets.",
        tone="info",
    ),
    unsafe_allow_html=True,
)
st.markdown(
    insight_chip(
        "<strong>Preprocessing.</strong> Numeric features: median imputation → StandardScaler. "
        "Categorical features: mode imputation → OneHotEncoder (handle_unknown='ignore'). "
        "Built with sklearn ColumnTransformer pipeline.",
        tone="info",
    ),
    unsafe_allow_html=True,
)
st.markdown(
    insight_chip(
        "<strong>Class imbalance.</strong> Addiction and Productivity models use "
        "class_weight='balanced_subsample' to handle unequal class distributions. "
        "Reported accuracy is on the stratified test set — not inflated training accuracy.",
    ),
    unsafe_allow_html=True,
)
