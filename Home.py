"""
Home.py — Behavioral Intelligence Advisor · Landing page + profile builder.

All metric cards include a scale= parameter explaining what the number means.
Gauges carry zone annotations (green/amber/red).
"""
from __future__ import annotations

from src import bootstrap  # noqa: F401

import streamlit as st

from src.charts import gauge, percentile_chart, radar_chart
from src.config import PALETTE
from src.inference import analyze_profile, load_artifacts, load_reference_dataset
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
from src.training import ensure_artifacts

st.set_page_config(
    page_title="Home — Behavioral Intelligence Advisor",
    page_icon="BI",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_styles()

PLOTLY_CONFIG = {"responsive": True, "displayModeBar": "hover",
                 "modeBarButtonsToRemove": ["lasso2d", "select2d"]}

with st.spinner("Loading behavioral intelligence models…"):
    try:
        ensure_artifacts()
        artifacts  = load_artifacts()
        reference  = load_reference_dataset()
    except Exception as exc:
        st.error(f"⚠️ Model loading failed: {exc}")
        st.stop()

metadata = artifacts["metadata"]
ensure_baseline(metadata, reference)

# ── Hero ─────────────────────────────────────────────────────────────────────
st.markdown(
    hero(
        eyebrow="AI-Driven Regional Aware & Smart Behavioral Analytics Prediction System",
        title="SmartInsight AI",
        body=(
            f"This research-grade behavioral intelligence platform integrates "
            f"{metadata['dataset_summary']['rows']:,} multi-source records across India, USA, "
            "and Global cohorts. Predict stress, addiction risk, and productivity. "
            "Understand the why. Simulate a healthier you."
        ),
    ),
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div style="margin: 0.2rem 0 1.6rem 0;">
      <span class="pill primary">Stress</span>
      <span class="pill accent">Addiction</span>
      <span class="pill secondary">Productivity</span>
      <span class="pill">Region-Aware</span>
      <span class="pill purple">Explainable AI</span>
      <span class="pill">16,000 Records</span>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Profile builder ───────────────────────────────────────────────────────────
st.markdown(
    section_header(
        "Your Profile",
        "Set your lifestyle inputs below. Click 'Analyze My Lifestyle' to run all three AI models.",
    ),
    unsafe_allow_html=True,
)
st.caption("All predictions and charts across the app update from this profile.")

defaults = metadata["defaults"]
options  = metadata["options"]

with st.expander("Demographics (optional)", expanded=False):
    demo_cols = st.columns(2)
    with demo_cols[0]:
        age    = st.slider("Age", 13, 80, int(defaults["Age"]), key="input_age")
        gender = st.selectbox(
            "Gender", options["Gender"],
            index=options["Gender"].index(defaults["Gender"])
            if defaults["Gender"] in options["Gender"] else 0,
            key="input_gender",
        )
    with demo_cols[1]:
        user_type = st.selectbox(
            "User Type", options["User_Type"],
            index=options["User_Type"].index(defaults.get("User_Type", "Mixed")),
            key="input_user_type",
        )
        region_group = st.selectbox(
            "Region", options["Region_Group"],
            index=options["Region_Group"].index(defaults.get("Region_Group", "Global")),
            key="input_region",
        )

st.markdown(
    score_legend([
        ("Screen / Social / Gaming / Work", PALETTE["primary"],    "Hours per day"),
        ("Sleep",                           PALETTE["secondary"],  "Hours per night · WHO recommends 7–9 h"),
        ("Notifications",                   PALETTE["accent"],     "Total push notifications per day"),
        ("Physical Activity",               PALETTE["secondary"],  "1 = inactive · 3 = moderate · 5 = very active"),
        ("Caffeine",                        PALETTE["foreground"], "mg per day · typical coffee ~100 mg"),
    ]),
    unsafe_allow_html=True,
)

slider_cols = st.columns(2)
with slider_cols[0]:
    screen_time  = st.slider("Screen Time (h/day)",      0.0, 14.0, float(defaults["Screen_Time"]),         0.1, key="input_screen")
    social_media = st.slider("Social Media Hours",        0.0,  8.0, float(defaults["Social_Media_Hours"]),  0.1, key="input_social")
    gaming       = st.slider("Gaming Hours",              0.0,  6.0, float(defaults["Gaming_Hours"]),         0.1, key="input_gaming")
    work_study   = st.slider("Work / Study Hours",        0.0, 10.0, float(defaults["Work_Study_Hours"]),     0.1, key="input_work")

with slider_cols[1]:
    sleep         = st.slider("Sleep Hours",               2.0, 11.0, float(defaults["Sleep_Hours"]),              0.1, key="input_sleep")
    notifications = st.slider("Notifications / Day",       0.0, 250.0, float(defaults["Notifications_Per_Day"]), 5.0, key="input_notifications")
    activity      = st.slider("Physical Activity (1–5)",   1.0,   5.0, float(defaults["Physical_Activity_Score"]), 0.1, key="input_activity")
    caffeine      = st.slider("Caffeine Intake (mg/day)",  0.0, 350.0, float(defaults["Caffeine_Intake"]),         5.0, key="input_caffeine")

age_group = (
    "Teen"        if age < 20 else
    "Young Adult" if age < 35 else
    "Adult"       if age < 55 else
    "Older Adult"
)

submitted = st.button("Analyze My Lifestyle", width="stretch")

if submitted:
    inputs = {
        "Age": age, "Gender": gender, "User_Type": user_type,
        "Region_Group": region_group, "Age_Group": age_group,
        "Screen_Time": screen_time, "Social_Media_Hours": social_media,
        "Gaming_Hours": gaming, "Work_Study_Hours": work_study,
        "Sleep_Hours": sleep, "Notifications_Per_Day": notifications,
        "Physical_Activity_Score": activity, "Caffeine_Intake": caffeine,
    }
    st.session_state.baseline_inputs = inputs
    st.session_state.analysis        = analyze_profile(inputs, reference)
    st.success("✓ Profile analyzed. Scroll down to see your results.")
    st.rerun()

analysis = st.session_state.analysis

# Headline chip
st.markdown(
    insight_chip(f"<strong>Current read.</strong> {analysis['headline']}"),
    unsafe_allow_html=True,
)
for warning in analysis["warnings"]:
    st.markdown(insight_chip(warning, tone="danger"), unsafe_allow_html=True)

# ── Behavioral overview cards ─────────────────────────────────────────────────
st.markdown(
    section_header(
        "Behavioral Overview",
        "Four key model outputs for your profile. Each card shows the score and its scale.",
    ),
    unsafe_allow_html=True,
)

card_cols_a = st.columns(2)
card_cols_a[0].markdown(
    metric_card(
        "Predicted Stress Level",
        f"{analysis['stress_level']:.2f}",
        delta=f"{analysis['stress_pct']:.0f}% of maximum stress",
        accent="danger" if analysis["stress_level"] >= 0.55 else "primary",
        scale="Scale 0.00–1.00 · 0.00 = no stress · 0.33 = low · 0.66 = moderate · 1.00 = extreme",
    ),
    unsafe_allow_html=True,
)
card_cols_a[1].markdown(
    metric_card(
        "Addiction Risk",
        analysis["addiction"]["label"],
        delta=f"Severity score: {analysis['addiction']['severity']:.2f} / 1.00",
        accent="warning" if analysis["addiction"]["label"] != "Low" else "secondary",
        scale="Categories: Low (0–0.33) · Moderate (0.33–0.66) · High (0.66–1.00)",
    ),
    unsafe_allow_html=True,
)

card_cols_b = st.columns(2)
card_cols_b[0].markdown(
    metric_card(
        "Productivity Outlook",
        f"{analysis['productivity']['productivity_score'] * 100:.0f} / 100",
        delta=f"Impact probability: {analysis['productivity']['impact_probability']:.0%}",
        accent="secondary" if analysis["productivity"]["productivity_score"] >= 0.6 else "warning",
        scale="100 = fully stable · 50 = borderline · <40 = likely impaired productivity",
    ),
    unsafe_allow_html=True,
)
card_cols_b[1].markdown(
    metric_card(
        "Behavioral Risk Index",
        f"{analysis['behavioral_risk_index']:.2f}",
        delta=f"Lifestyle Score: {analysis['lifestyle_score']['total']:.0f} / 100",
        accent="danger" if analysis["behavioral_risk_index"] > 0.45 else "accent",
        scale=(
            "BRI 0.00–1.00 · formula: 0.35×screen + 0.30×stress − 0.20×sleep + 0.15×social · "
            "all inputs normalised to [0,1]"
        ),
    ),
    unsafe_allow_html=True,
)

# ── Lifestyle gauges ──────────────────────────────────────────────────────────
st.markdown(
    section_header(
        "Lifestyle Gauges",
        "Semi-circular gauges · zone colours: 🟢 0.00–0.33 low · 🟡 0.33–0.66 moderate · 🔴 0.66–1.00 high.",
    ),
    unsafe_allow_html=True,
)
st.markdown(
    scale_note(
        "All gauges run 0.00 → 1.00. For Stress and BRI: outer edge = worst. "
        "For Productivity: outer edge = best (score is inverted risk)."
    ),
    unsafe_allow_html=True,
)

gauge_cols = st.columns(3)
gauge_cols[0].plotly_chart(
    gauge(
        "Predicted Stress",
        analysis["stress_level"], 0.0, 1.0,
        PALETTE["danger"] if analysis["stress_level"] >= 0.55 else PALETTE["accent"],
        scale_label="0.00 = calm · 0.33 = low · 0.66 = moderate · 1.00 = extreme",
    ),
    width="stretch", config=PLOTLY_CONFIG,
)
gauge_cols[1].plotly_chart(
    gauge(
        "Productivity Outlook",
        analysis["productivity"]["productivity_score"], 0.0, 1.0,
        PALETTE["secondary"],
        scale_label="0.00 = fully impacted · 1.00 = fully stable & productive",
    ),
    width="stretch", config=PLOTLY_CONFIG,
)
gauge_cols[2].plotly_chart(
    gauge(
        "Behavioral Risk Index",
        analysis["behavioral_risk_index"], 0.0, 1.0,
        PALETTE["danger"] if analysis["behavioral_risk_index"] > 0.45 else PALETTE["primary"],
        scale_label="0.00 = minimal risk · 0.45 = elevated · 1.00 = maximum risk",
    ),
    width="stretch", config=PLOTLY_CONFIG,
)

# ── Percentile chart ──────────────────────────────────────────────────────────
st.markdown(
    section_header(
        "Where You Sit vs the Cohort",
        f"Your percentile rank within the full {metadata['dataset_summary']['rows']:,}-record dataset. "
        "50th percentile = exactly average. For risk metrics (stress, screen time), lower is better.",
    ),
    unsafe_allow_html=True,
)
st.markdown(
    score_legend([
        ("≥75th (high)",   PALETTE["danger"],    "You are in the top 25% of the cohort on this metric"),
        ("50–74th (above avg)", PALETTE["accent"], "Above average"),
        ("<50th (below avg)",   PALETTE["secondary"], "Below average (better for risk metrics)"),
    ]),
    unsafe_allow_html=True,
)
if analysis.get("percentiles"):
    st.plotly_chart(
        percentile_chart(analysis["percentiles"]),
        width="stretch", config=PLOTLY_CONFIG,
    )

# ── Radar chart ────────────────────────────────────────────────────────────────
st.markdown(
    section_header(
        "Lifestyle Balance vs Cohort",
        "Radar compares your profile to the cohort average. "
        "OUTER edge = better outcome on all axes. Stress and Screen Time are inverted so outer = healthier.",
    ),
    unsafe_allow_html=True,
)
st.markdown(
    scale_note("Scale 0–100 · 100 = optimal · 0 = worst case · Blue = your profile · Amber dashed = cohort average"),
    unsafe_allow_html=True,
)
st.plotly_chart(
    radar_chart(analysis["radar"]),
    width="stretch", config=PLOTLY_CONFIG,
)

# ── Navigation footer ─────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="footer-note">
      <strong>Navigate the full advisor using the left sidebar:</strong><br>
      📍 <strong>Region-Aware Analytics</strong> — India vs USA vs Global comparison ·
      👥 <strong>Students vs Professionals</strong> — segment behavioural profiles ·
      🤖 <strong>AI Risk Prediction</strong> — model metrics + live gauges ·
      🧩 <strong>Behavioral Archetypes</strong> — which cluster are you in? ·
      🔍 <strong>Explainable AI Lab</strong> — feature importance + sensitivity ·
      🎛️ <strong>Scenario Simulation</strong> — what-if lifestyle changes ·
      💡 <strong>Smart Insight Engine</strong> — personalised recommendations
    </div>
    """,
    unsafe_allow_html=True,
)
