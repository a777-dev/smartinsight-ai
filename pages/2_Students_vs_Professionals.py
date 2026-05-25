from __future__ import annotations
from src import bootstrap  # noqa: F401
import streamlit as st
from src.analytics import (addiction_distribution, burnout_share, sleep_deficit_share, user_insight_cards, user_summary)
from src.charts import addiction_distribution_chart, grouped_bar, violin_by_region
from src.config import PALETTE, USER_PALETTE
from src.inference import load_artifacts, load_reference_dataset
from src.session import ensure_baseline
from src.styles import apply_styles, divider, hero, insight_chip, metric_card, scale_note, score_legend, section_header

st.set_page_config(page_title="Students vs Professionals — Behavioral Intelligence Advisor", layout="wide")
apply_styles()
PLOTLY_CONFIG = {"responsive": True, "displayModeBar": "hover", "modeBarButtonsToRemove": ["lasso2d", "select2d"]}

try:
    artifacts = load_artifacts()
    dataset   = load_reference_dataset()
    ensure_baseline(artifacts["metadata"], dataset)
except Exception as exc:
    st.error(f"⚠️ Could not load data: {exc}. Please reload the Home page first.")
    st.stop()

st.markdown(hero(eyebrow="Page 03 — Segment Analysis", title="Students vs Professionals.",
    body="Mirror behavioral signatures across academic and workforce populations. "
         "Compare burnout, sleep deficit, screen time, and addiction patterns side by side."), unsafe_allow_html=True)

summary = user_summary(dataset).set_index("User_Type")

# ── Scale legend ──────────────────────────────────────────────────────────────
st.markdown(score_legend([
    ("Students",      USER_PALETTE["Student"],      "Academic population (university/school cohort)"),
    ("Professionals", USER_PALETTE["Professional"], "Workforce population (employed adults)"),
    ("Mixed",         USER_PALETTE["Mixed"],        "General / unclassified users"),
]), unsafe_allow_html=True)

# ── Split metric cards ────────────────────────────────────────────────────────
st.markdown(section_header("Cohort Snapshot", "Side-by-side average metrics per user type. "
    "Metric cards show dataset means — hover charts for full distributions."), unsafe_allow_html=True)

split = st.columns(2)
def render_segment(column, label: str, accent: str) -> None:
    if label not in summary.index:
        return
    row = summary.loc[label]
    with column:
        color = USER_PALETTE.get(label, PALETTE["primary"])
        st.markdown(f"<h3 style='margin:0.2rem 0 0.8rem;border-bottom:3px solid {color};padding-bottom:0.4rem'>{label}s</h3>", unsafe_allow_html=True)
        st.markdown(metric_card("Avg Screen Time", f"{row['Screen_Time']:.1f} h",
            delta=f"Social media: {row['Social_Media_Hours']:.1f} h/day", accent=accent,
            scale="Hours per day · WHO guideline: ≤4 h recreational screen for adults"), unsafe_allow_html=True)
        st.markdown(metric_card("Avg Sleep", f"{row['Sleep_Hours']:.1f} h",
            delta=f"Physical activity: {row['Physical_Activity_Score']:.1f} / 5", accent=accent,
            scale="Hours per night · Optimal: 7–9 h · <6 h = clinical deficit"), unsafe_allow_html=True)
        st.markdown(metric_card("Stress Level", f"{row['Stress_Level_Norm']:.2f}",
            delta=f"Behavioral Risk Index: {row['Behavioral_Risk_Index_Recomputed']:.2f}", accent=accent,
            scale="Normalised 0.00–1.00 · 0.00 = calm · 0.33 = low · 0.66 = moderate · 1.00 = extreme"), unsafe_allow_html=True)
        st.markdown(metric_card("Work / Study Hours", f"{row['Work_Study_Hours']:.1f} h",
            delta=f"Notifications/day: {row['Notifications_Per_Day']:.0f}", accent=accent,
            scale="Hours per day dedicated to work or study tasks"), unsafe_allow_html=True)

render_segment(split[0], "Student", "primary")
render_segment(split[1], "Professional", "warning")

# ── Comparative bar chart ─────────────────────────────────────────────────────
st.markdown(section_header("Lifestyle Hours Comparison",
    "Dataset means per group. Each bar shows average hours per day for that metric."), unsafe_allow_html=True)
st.markdown(scale_note("Y-axis: Average hours per day. "
    "Sleep is a positive metric — higher is better. "
    "Screen Time and Social Media: lower is generally better for stress outcomes. "
    "Hover any bar for the exact figure."), unsafe_allow_html=True)

palette = {
    "Screen_Time":        USER_PALETTE["Student"],
    "Sleep_Hours":        USER_PALETTE["Mixed"],
    "Work_Study_Hours":   USER_PALETTE["Student"],
    "Social_Media_Hours": USER_PALETTE["Professional"],
}
st.plotly_chart(grouped_bar(user_summary(dataset), "User_Type",
    ["Screen_Time", "Sleep_Hours", "Work_Study_Hours", "Social_Media_Hours"],
    palette, "Lifestyle Hours by User Type",
    y_label="Average hours per day", x_label="User Type", y_suffix=" h"),
    width="stretch", config=PLOTLY_CONFIG)

# ── Risk metrics bar chart ────────────────────────────────────────────────────
st.markdown(divider("Risk & Wellness Indicators"), unsafe_allow_html=True)
st.markdown(scale_note("Stress: normalised 0.00–1.00. BRI: Behavioral Risk Index 0.00–1.00 (higher = more risk). "
    "Addiction Level: normalised 0.00–1.00 (higher = stronger dependency signals). "
    "Physical Activity: 1–5 scale (5 = very active)."), unsafe_allow_html=True)
risk_palette = {
    "Stress_Level_Norm":                PALETTE["danger"],
    "Behavioral_Risk_Index_Recomputed": PALETTE["accent"],
    "Addiction_Level_Norm":             USER_PALETTE["Student"],
    "Physical_Activity_Score":          PALETTE["secondary"],
}
st.plotly_chart(grouped_bar(user_summary(dataset), "User_Type",
    ["Stress_Level_Norm", "Behavioral_Risk_Index_Recomputed", "Addiction_Level_Norm", "Physical_Activity_Score"],
    risk_palette, "Risk & Wellness Indicators by User Type",
    y_label="Normalised score (0.00–1.00 unless noted)", x_label="User Type"),
    width="stretch", config=PLOTLY_CONFIG)

# ── Burnout & deficit insight chips ──────────────────────────────────────────
st.markdown(divider("Burnout & Sleep Deficit"), unsafe_allow_html=True)
st.markdown(scale_note("Burnout share = % of group with Stress_Level_Norm > 0.40. "
    "Sleep deficit share = % of group sleeping fewer than 6 h/night."), unsafe_allow_html=True)

burnout = burnout_share(dataset, "User_Type")
deficit = sleep_deficit_share(dataset, "User_Type")
chip_cols = st.columns(3)
for i, row in burnout.iterrows():
    chip_cols[i % 3].markdown(insight_chip(
        f"<strong>{row['User_Type']}.</strong> {row['burnout_share']*100:.1f}% in the high-stress band "
        f"(Stress > 0.40).", tone="warning"), unsafe_allow_html=True)
for i, row in deficit.iterrows():
    chip_cols[i % 3].markdown(insight_chip(
        f"<strong>{row['User_Type']}.</strong> {row['deficit_share']*100:.1f}% sleep below 6 h/night.",
        tone="danger"), unsafe_allow_html=True)

# ── Addiction composition ─────────────────────────────────────────────────────
st.markdown(section_header("Addiction Category Composition",
    "What proportion of each user type falls into Low / Moderate / High addiction severity."), unsafe_allow_html=True)
st.markdown(score_legend([
    ("Low",      "#10B981", "0–33 percentile of Addiction_Level_Norm — minimal dependency"),
    ("Moderate", "#F59E0B", "34–66 percentile — some concerning patterns"),
    ("High",     "#EF4444", "67–100 percentile — strong dependency signals"),
]), unsafe_allow_html=True)
st.markdown(scale_note("Y-axis: Percentage of the user-type group in that addiction category. "
    "Bars within each group sum to 100%."), unsafe_allow_html=True)
addiction_share = addiction_distribution(dataset, "User_Type")
st.plotly_chart(addiction_distribution_chart(addiction_share, "User_Type",
    "Addiction Category Share by User Type"), width="stretch", config=PLOTLY_CONFIG)

# ── Insight cards ─────────────────────────────────────────────────────────────
st.markdown(divider("Behavioral Differences"), unsafe_allow_html=True)
for card in user_insight_cards(dataset):
    st.markdown(insight_chip(f"<strong>{card['title']}.</strong> {card['body']}"), unsafe_allow_html=True)
