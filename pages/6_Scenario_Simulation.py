from __future__ import annotations
from src import bootstrap  # noqa: F401
import streamlit as st
from src.charts import before_after_chart
from src.inference import analyze_profile, load_artifacts, load_reference_dataset
from src.session import ensure_baseline
from src.styles import apply_styles, divider, hero, insight_chip, metric_card, scale_note, score_legend, section_header

st.set_page_config(page_title="Scenario Simulation — Behavioral Intelligence Advisor", layout="wide")
apply_styles()
PLOTLY_CONFIG = {"responsive": True, "displayModeBar": "hover", "modeBarButtonsToRemove": ["lasso2d", "select2d"]}

try:
    artifacts        = load_artifacts()
    reference        = load_reference_dataset()
    baseline_analysis = ensure_baseline(artifacts["metadata"], reference)
    baseline_inputs  = st.session_state.baseline_inputs
except Exception as exc:
    st.error(f"⚠️ Could not load models: {exc}. Please reload the Home page first.")
    st.stop()

st.markdown(hero(eyebrow="Page 07 — What-If Simulator", title="Scenario Simulation Engine.",
    body="Move the sliders to ask: what happens if I sleep more? Cut screen time? "
         "Every change re-runs all three AI models in real time. "
         "Delta cards show the model output change vs your baseline profile."), unsafe_allow_html=True)

with st.expander("ℹ️  How to read this page", expanded=False):
    st.markdown("""
**Delta cards (top section):** Show the change in each predicted score vs your baseline profile.
- **Positive Stress Δ** (e.g. +0.04) = this scenario predicts *more* stress than your baseline
- **Negative Stress Δ** (e.g. −0.08) = this scenario predicts *less* stress — an improvement

**Score directions:**
| Metric | Lower is better | Higher is better |
|---|---|---|
| Stress (0.00–1.00) | ✅ | — |
| Addiction Severity (0.00–1.00) | ✅ | — |
| Productivity Score (0–100) | — | ✅ |
| BRI — Behavioral Risk Index (0.00–1.00) | ✅ | — |

**Before vs After chart:** All scores converted to a unified 0–100 scale for side-by-side comparison.
For risk metrics (Stress, Addiction, BRI), lower bars = better. For Productivity/Lifestyle, higher = better.
    """)

# ── Sliders ───────────────────────────────────────────────────────────────────
st.markdown(section_header("Adjust Your Scenario",
    "Sliders start at your baseline profile values. Change any to simulate a different lifestyle."), unsafe_allow_html=True)
st.markdown(score_legend([
    ("Sleep",        "#10B981", "h/night · 7–9 h is optimal"),
    ("Screen Time",  "#EF4444", "h/day · >8 h correlates with burnout"),
    ("Notifications","#F59E0B", "per day · >180 is high digital fatigue load"),
    ("Activity",     "#10B981", "1–5 scale · 5 = very active"),
    ("Caffeine",     "#6B7280", "mg/day · typical coffee ~100 mg"),
]), unsafe_allow_html=True)

if "sim_inputs" not in st.session_state:
    st.session_state.sim_inputs = dict(baseline_inputs)

sim_cols = st.columns(2)
with sim_cols[0]:
    sleep         = st.slider("Sleep Hours (h/night — optimal: 7–9)", 2.0, 11.0, float(st.session_state.sim_inputs["Sleep_Hours"]), 0.1)
    screen        = st.slider("Screen Time (h/day — >8 h = burnout risk)", 0.0, 14.0, float(st.session_state.sim_inputs["Screen_Time"]), 0.1)
    social        = st.slider("Social Media Hours (h/day)", 0.0, 8.0, float(st.session_state.sim_inputs["Social_Media_Hours"]), 0.1)
    notifications = st.slider("Notifications / Day (>180 = digital fatigue zone)", 0.0, 250.0, float(st.session_state.sim_inputs["Notifications_Per_Day"]), 5.0)
with sim_cols[1]:
    activity  = st.slider("Physical Activity (1 = inactive · 5 = very active)", 1.0, 5.0, float(st.session_state.sim_inputs["Physical_Activity_Score"]), 0.1)
    caffeine  = st.slider("Caffeine Intake mg/day (typical coffee = 100 mg)", 0.0, 350.0, float(st.session_state.sim_inputs["Caffeine_Intake"]), 5.0)
    gaming    = st.slider("Gaming Hours (h/day)", 0.0, 6.0, float(st.session_state.sim_inputs["Gaming_Hours"]), 0.1)
    work      = st.slider("Work / Study Hours (h/day)", 0.0, 10.0, float(st.session_state.sim_inputs["Work_Study_Hours"]), 0.1)

reset_col, _ = st.columns([1, 3])
with reset_col:
    if st.button("Reset to Baseline", width="stretch"):
        st.session_state.sim_inputs = dict(baseline_inputs)
        st.rerun()

scenario_inputs = dict(baseline_inputs)
scenario_inputs.update({"Sleep_Hours": sleep, "Screen_Time": screen, "Social_Media_Hours": social,
    "Notifications_Per_Day": notifications, "Physical_Activity_Score": activity,
    "Caffeine_Intake": caffeine, "Gaming_Hours": gaming, "Work_Study_Hours": work})
st.session_state.sim_inputs = scenario_inputs
scenario = analyze_profile(scenario_inputs, reference)

# ── Delta cards ───────────────────────────────────────────────────────────────
st.markdown(section_header("Predicted Changes vs Your Baseline",
    "Each card shows: the delta (change) from your baseline, and the new absolute value. "
    "Green = improvement. Red = worsening."), unsafe_allow_html=True)
st.markdown(scale_note(
    "Stress Δ and BRI Δ: negative = improvement (risk decreasing). "
    "Productivity Δ: positive = improvement. "
    "Addiction Δ: negative = improvement. "
    "All deltas on their native 0.00–1.00 scale."), unsafe_allow_html=True)

stress_d = scenario["stress_level"] - baseline_analysis["stress_level"]
addict_d = scenario["addiction"]["severity"] - baseline_analysis["addiction"]["severity"]
prod_d   = scenario["productivity"]["productivity_score"] - baseline_analysis["productivity"]["productivity_score"]
bri_d    = scenario["behavioral_risk_index"] - baseline_analysis["behavioral_risk_index"]

delta_top = st.columns(2)
delta_top[0].markdown(metric_card("Stress Δ", f"{stress_d:+.3f}",
    delta=f"Now {scenario['stress_level']:.2f} / 1.00 · baseline {baseline_analysis['stress_level']:.2f}",
    accent="secondary" if stress_d < 0 else "danger",
    scale="0.00–1.00 · negative delta = less stress (improvement)"), unsafe_allow_html=True)
delta_top[1].markdown(metric_card("Addiction Severity Δ", f"{addict_d:+.3f}",
    delta=f"Now {scenario['addiction']['severity']:.2f} · predicted class: {scenario['addiction']['label']}",
    accent="secondary" if addict_d < 0 else "warning",
    scale="0.00–1.00 · negative delta = lower addiction severity (improvement)"), unsafe_allow_html=True)

delta_bot = st.columns(2)
delta_bot[0].markdown(metric_card("Productivity Δ", f"{prod_d:+.3f}",
    delta=f"Now {scenario['productivity']['productivity_score']*100:.0f} / 100",
    accent="secondary" if prod_d > 0 else "danger",
    scale="0.00–1.00 · positive delta = more productive (improvement)"), unsafe_allow_html=True)
delta_bot[1].markdown(metric_card("BRI Δ", f"{bri_d:+.3f}",
    delta=f"Now {scenario['behavioral_risk_index']:.2f} / 1.00 · baseline {baseline_analysis['behavioral_risk_index']:.2f}",
    accent="secondary" if bri_d < 0 else "danger",
    scale="Behavioral Risk Index 0.00–1.00 · negative = lower risk (improvement)"), unsafe_allow_html=True)

# ── Before / after chart ──────────────────────────────────────────────────────
st.markdown(section_header("Before vs After — All Metrics",
    "Unified 0–100 scale for visual comparison. "
    "For risk metrics (Stress, Addiction, BRI): shorter bar = better. "
    "For Productivity and Lifestyle Score: taller bar = better."), unsafe_allow_html=True)
st.markdown(scale_note(
    "All five metrics converted to a common 0–100 scale. "
    "Amber = your current baseline. Blue = this simulated scenario. "
    "Direction labels below each metric name indicate which direction is better."), unsafe_allow_html=True)
st.plotly_chart(before_after_chart(baseline_analysis, scenario), width="stretch", config=PLOTLY_CONFIG)

# ── Archetype shift ───────────────────────────────────────────────────────────
if scenario["cluster"]["label"] != baseline_analysis["cluster"]["label"]:
    st.markdown(insight_chip(
        f"<strong>Archetype shift detected.</strong> This scenario moves you from "
        f"<strong>{baseline_analysis['cluster']['label']}</strong> to "
        f"<strong>{scenario['cluster']['label']}</strong>. "
        "Visit the Behavioral Archetypes page to understand what this means.", tone="warning"),
        unsafe_allow_html=True)
else:
    st.markdown(insight_chip(
        f"<strong>Archetype unchanged.</strong> You remain in the "
        f"<strong>{scenario['cluster']['label']}</strong> cluster. "
        "Larger lifestyle changes may be needed to shift archetypes."), unsafe_allow_html=True)

st.markdown(divider("Scenario Insights"), unsafe_allow_html=True)
messages = scenario["warnings"] if scenario["warnings"] else [scenario["headline"]]
for msg in messages:
    st.markdown(insight_chip(msg), unsafe_allow_html=True)
