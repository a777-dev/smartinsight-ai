from __future__ import annotations
from src import bootstrap  # noqa: F401
import streamlit as st
from src.inference import load_artifacts, load_reference_dataset
from src.insights import generate_insights
from src.session import ensure_baseline
from src.styles import apply_styles, divider, hero, insight_chip, metric_card, scale_note, score_legend, section_header

st.set_page_config(page_title="Smart Insight Engine — Behavioral Intelligence Advisor", layout="wide")
apply_styles()

try:
    artifacts = load_artifacts()
    reference = load_reference_dataset()
    analysis  = ensure_baseline(artifacts["metadata"], reference)
except Exception as exc:
    st.error(f"⚠️ Could not load models: {exc}. Please reload the Home page first.")
    st.stop()

st.markdown(hero(eyebrow="Page 08 — AI Recommendations", title="Smart Insight Engine.",
    body="Personalized, model-aware recommendations. The engine blends rule-based triggers "
         "(sleep thresholds, screen-time ceilings) with live model outputs to return 3–5 "
         "highest-impact actions for your current profile."), unsafe_allow_html=True)

# ── Lifestyle Score snapshot ──────────────────────────────────────────────────
st.markdown(section_header("Lifestyle Score Snapshot",
    "Composite wellness score (0–100). Weighted from Sleep (30%), Screen Time (25%), Stress (25%), Productivity (20%). "
    "Higher is always better."), unsafe_allow_html=True)
st.markdown(score_legend([
    ("80–100", "#10B981", "Excellent — maintain these habits"),
    ("60–79",  "#3B82F6", "Good — minor improvements will push you higher"),
    ("40–59",  "#F59E0B", "Moderate — 1–2 key changes will make a measurable difference"),
    ("0–39",   "#EF4444", "Needs attention — prioritize sleep and screen-time reduction"),
]), unsafe_allow_html=True)
st.markdown(scale_note(
    "Lifestyle Score = (Sleep Score × 0.30) + (Screen Score × 0.25) + (Stress Score × 0.25) + (Productivity × 0.20). "
    "Each component is individually scaled 0–100 before weighting."), unsafe_allow_html=True)

components = analysis["lifestyle_score"]["components"]
total_score = analysis["lifestyle_score"]["total"]

snap_top = st.columns(2)
snap_top[0].markdown(metric_card("Lifestyle Score", f"{total_score:.0f} / 100",
    delta=analysis["headline"],
    accent="secondary" if total_score >= 70 else "warning" if total_score >= 50 else "danger",
    scale="0–100 · 100 = optimal lifestyle · <40 = significant improvement needed"), unsafe_allow_html=True)

component_items = list(components.items())
snap_top[1].markdown(metric_card(
    component_items[0][0], f"{component_items[0][1]:.0f} / 100",
    delta=f"Weight: {['30%','25%','25%','20%'][0]} of total score",
    accent="secondary" if component_items[0][1] >= 60 else "warning" if component_items[0][1] >= 40 else "danger",
    scale="0–100 component score · contributes 30% to your Lifestyle Score"), unsafe_allow_html=True)

snap_bot = st.columns(3)
weights = ["25%", "25%", "20%"]
for i, (name, value) in enumerate(component_items[1:]):
    snap_bot[i % 3].markdown(metric_card(name, f"{value:.0f} / 100",
        delta=f"Weight: {weights[i]} of total score",
        accent="secondary" if value >= 60 else "warning" if value >= 40 else "danger",
        scale=f"0–100 · higher is better · contributes {weights[i]} to Lifestyle Score"), unsafe_allow_html=True)

# ── Model outputs ─────────────────────────────────────────────────────────────
st.markdown(divider("Current Model Predictions"), unsafe_allow_html=True)
st.markdown(scale_note(
    "All risk scores on their native scale. "
    "Stress: 0.00–1.00 (lower = better). Addiction: Low/Moderate/High. "
    "Productivity: 0–100 (higher = better). BRI: 0.00–1.00 (lower = better)."), unsafe_allow_html=True)

pred_cols = st.columns(4)
pred_cols[0].markdown(metric_card("Stress", f"{analysis['stress_level']:.2f}",
    delta=f"{analysis['stress_pct']:.0f}% of maximum",
    accent="danger" if analysis["stress_level"] >= 0.55 else "warning" if analysis["stress_level"] >= 0.33 else "secondary",
    scale="0.00–1.00 · 0.33 = low · 0.55 = high"), unsafe_allow_html=True)
pred_cols[1].markdown(metric_card("Addiction Risk", analysis["addiction"]["label"],
    delta=f"Severity: {analysis['addiction']['severity']:.2f} / 1.00",
    accent="danger" if analysis["addiction"]["label"] == "High" else "warning" if analysis["addiction"]["label"] == "Moderate" else "secondary",
    scale="Low (0–0.33) · Moderate (0.33–0.66) · High (0.66–1.00)"), unsafe_allow_html=True)
pred_cols[2].markdown(metric_card("Productivity", f"{analysis['productivity']['productivity_score']*100:.0f} / 100",
    delta=f"Impact probability: {analysis['productivity']['impact_probability']:.0%}",
    accent="secondary" if analysis["productivity"]["productivity_score"] >= 0.6 else "warning",
    scale="100 = fully stable · <40 = significant impairment likely"), unsafe_allow_html=True)
pred_cols[3].markdown(metric_card("BRI", f"{analysis['behavioral_risk_index']:.3f}",
    delta=f"Archetype: {analysis['cluster']['label']}",
    accent="danger" if analysis["behavioral_risk_index"] > 0.45 else "accent",
    scale="Behavioral Risk Index 0.00–1.00 · <0.25 = healthy range"), unsafe_allow_html=True)

# ── Recommended actions ───────────────────────────────────────────────────────
st.markdown(section_header("Recommended Actions",
    "3–5 highest-impact interventions for your current profile. "
    "Actions are ranked by predicted model sensitivity — highest-leverage changes first."), unsafe_allow_html=True)

insights = generate_insights(
    profile=analysis["profile"],
    stress_norm=analysis["stress_level"],
    productivity_score=analysis["productivity"]["productivity_score"],
    addiction_label=analysis["addiction"]["label"],
    behavioral_risk_index=analysis["behavioral_risk_index"],
    cluster_label=analysis["cluster"]["label"],
)
for index, message in enumerate(insights, start=1):
    tone = "danger" if any(w in message.lower() for w in ["burnout", "critical", "high"]) else \
           "warning" if any(w in message.lower() for w in ["risk", "below", "impair"]) else "default"
    st.markdown(insight_chip(f"<strong>Action {index}.</strong> {message}", tone=tone), unsafe_allow_html=True)

# ── Methodology ───────────────────────────────────────────────────────────────
st.markdown(divider("Engine Methodology"), unsafe_allow_html=True)
st.markdown(insight_chip(
    "<strong>How insights are generated.</strong> The engine applies explicit behavioral rules "
    "(sleep < 6 h, screen > 8 h, notifications > 180, caffeine > 200 mg + sleep deficit) against your "
    "current profile. These are cross-referenced with the three ML model outputs (stress regressor, "
    "addiction classifier, productivity classifier) to select the highest-impact actionable recommendations. "
    "At most 5 insights are returned, ordered by estimated lifestyle-score improvement potential.", tone="info"),
    unsafe_allow_html=True)
st.markdown(insight_chip(
    "<strong>How to act on these.</strong> Use the Scenario Simulation page to test each recommendation. "
    "Adjust the corresponding slider and observe the model delta. Focus on the change with the largest "
    "negative Stress Δ or largest positive Productivity Δ first.", tone="info"),
    unsafe_allow_html=True)
