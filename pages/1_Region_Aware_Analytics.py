"""
pages/1_Region_Aware_Analytics.py

Region-Aware Analytics — Compare India, USA, Global cohorts.
All charts carry axis labels, units, and scale notes.
"""
from __future__ import annotations

from src import bootstrap  # noqa: F401

import streamlit as st

from src.analytics import (
    addiction_distribution,
    region_insight_cards,
    region_summary,
    sleep_deficit_share,
)
from src.charts import (
    addiction_distribution_chart,
    choropleth_risk_map,
    grouped_bar,
    violin_by_region,
)
from src.config import PALETTE, REGION_PALETTE
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

st.set_page_config(page_title="Region Analytics — Behavioral Intelligence Advisor", layout="wide")
apply_styles()

PLOTLY_CONFIG = {"responsive": True, "displayModeBar": "hover",
                 "modeBarButtonsToRemove": ["lasso2d", "select2d"]}

try:
    artifacts = load_artifacts()
    dataset   = load_reference_dataset()
    ensure_baseline(artifacts["metadata"], dataset)
except Exception as exc:
    st.error(f"⚠️ Could not load data: {exc}. Please reload the Home page first.")
    st.stop()

summary = region_summary(dataset)

# ── Hero ─────────────────────────────────────────────────────────────────────
st.markdown(
    hero(
        eyebrow="Page 02 — Region-Aware Analytics",
        title="Region-Aware Analytics.",
        body=(
            "Compare India, USA, and Global cohorts on stress, sleep, screen time, "
            "social media intensity, addiction patterns, and physical activity. "
            "Each metric is described with its scale and units."
        ),
    ),
    unsafe_allow_html=True,
)

# ── Region colour legend ───────────────────────────────────────────────────────
st.markdown(
    score_legend([
        ("India",  REGION_PALETTE["India"],  "Indian user cohort from dataset sources"),
        ("USA",    REGION_PALETTE["USA"],    "United States user cohort"),
        ("Global", REGION_PALETTE["Global"], "International / unclassified cohort"),
    ]),
    unsafe_allow_html=True,
)

# ── Global Risk Map ───────────────────────────────────────────────────────────
st.markdown(
    section_header(
        "Global Behavioral Risk Map",
        "Interactive world map — hover India or USA to explore all key behavioral metrics. "
        "Color encodes the Behavioral Risk Index (0.00 = low risk · 1.00 = high risk). "
        "Global cohort stats shown as a floating annotation.",
    ),
    unsafe_allow_html=True,
)
st.plotly_chart(
    choropleth_risk_map(summary),
    width="stretch", config=PLOTLY_CONFIG,
)

# ── Digital lifestyle averages ────────────────────────────────────────────────
st.markdown(
    section_header(
        "Digital Lifestyle Averages by Region",
        "Dataset means per region · each bar shows the average hours per day for that metric.",
    ),
    unsafe_allow_html=True,
)
st.markdown(
    scale_note(
        "Y-axis: Average hours per day (0–14 h for screen time, 0–8 h for social media, 0–11 h for sleep). "
        "Hover any bar for the exact figure. Sleep is a positive metric — lower than 7 h indicates deficit."
    ),
    unsafe_allow_html=True,
)

palette_digital = {
    "Screen_Time":       REGION_PALETTE["India"],
    "Social_Media_Hours": REGION_PALETTE["USA"],
    "Sleep_Hours":        REGION_PALETTE["Global"],
}
st.plotly_chart(
    grouped_bar(
        summary,
        "Region_Group",
        ["Screen_Time", "Social_Media_Hours", "Sleep_Hours"],
        palette_digital,
        "Digital Lifestyle Averages by Region",
        y_label="Average hours per day",
        x_label="Region Group",
        y_suffix=" h",
    ),
    width="stretch", config=PLOTLY_CONFIG,
)

# ── Stress & notifications distributions ─────────────────────────────────────
st.markdown(
    section_header(
        "Stress & Notification Distributions",
        "Violin plots show the FULL distribution, not just the mean — "
        "the wider the violin, the more users are at that value.",
    ),
    unsafe_allow_html=True,
)
st.markdown(
    scale_note(
        "Stress: normalised 0.00–1.00 · 0.00 = no stress · 1.00 = maximum stress. "
        "Notifications: raw count per day · typical range 0–250. "
        "Inner box = interquartile range (25th–75th %ile). Centre line = median."
    ),
    unsafe_allow_html=True,
)

violin_cols = st.columns(2)
with violin_cols[0]:
    st.plotly_chart(
        violin_by_region(dataset, "Stress_Level_Norm", "Stress Level Distribution by Region"),
        width="stretch", config=PLOTLY_CONFIG,
    )
with violin_cols[1]:
    st.plotly_chart(
        violin_by_region(dataset, "Notifications_Per_Day", "Daily Notifications by Region"),
        width="stretch", config=PLOTLY_CONFIG,
    )

# ── Sleep & physical activity distributions ───────────────────────────────────
st.markdown(divider("Sleep & Activity"), unsafe_allow_html=True)
st.markdown(
    scale_note(
        "Sleep: hours per night · WHO recommends 7–9 h for adults. "
        "Physical Activity Score: 1 = inactive · 3 = moderate · 5 = very active."
    ),
    unsafe_allow_html=True,
)
act_cols = st.columns(2)
with act_cols[0]:
    st.plotly_chart(
        violin_by_region(dataset, "Sleep_Hours", "Sleep Duration by Region"),
        width="stretch", config=PLOTLY_CONFIG,
    )
with act_cols[1]:
    st.plotly_chart(
        violin_by_region(dataset, "Physical_Activity_Score", "Physical Activity Score by Region"),
        width="stretch", config=PLOTLY_CONFIG,
    )

# ── Addiction composition ──────────────────────────────────────────────────────
st.markdown(
    section_header(
        "Addiction Category Composition by Region",
        "What proportion of each regional cohort falls into Low / Moderate / High addiction severity.",
    ),
    unsafe_allow_html=True,
)
st.markdown(
    score_legend([
        ("Low",      "#10B981", "Minimal digital dependency signals"),
        ("Moderate", "#F59E0B", "Watch-list — some concerning patterns"),
        ("High",     "#EF4444", "Strong dependency signals — intervention recommended"),
    ]),
    unsafe_allow_html=True,
)
st.markdown(
    scale_note(
        "Y-axis: Percentage of the regional group in each addiction category (bars sum to 100%). "
        "Addiction category derived from Addiction_Level score thresholds (Low: 0–0.33, Moderate: 0.33–0.66, High: 0.66–1.00)."
    ),
    unsafe_allow_html=True,
)

addiction_share = addiction_distribution(dataset, "Region_Group")
st.plotly_chart(
    addiction_distribution_chart(
        addiction_share,
        "Region_Group",
        "Addiction Category Share by Region",
    ),
    width="stretch", config=PLOTLY_CONFIG,
)

# ── Sleep deficit ──────────────────────────────────────────────────────────────
st.markdown(
    section_header(
        "Sleep Deficit Prevalence",
        "Proportion of users sleeping fewer than 6 hours per night (clinical sleep deficit threshold).",
    ),
    unsafe_allow_html=True,
)
deficit = sleep_deficit_share(dataset, "Region_Group")

deficit_cols = st.columns(len(deficit))
for col, row in zip(deficit_cols, deficit.itertuples()):
    col.markdown(
        metric_card(
            f"{row.Region_Group} Sleep Deficit",
            f"{row.deficit_share * 100:.1f}%",
            delta="of users sleep < 6 h/night",
            accent="danger" if row.deficit_share > 0.4 else "warning" if row.deficit_share > 0.25 else "secondary",
            scale="Scale: 0% = no deficit · >40% = population-level concern",
        ),
        unsafe_allow_html=True,
    )

# ── Behavioural risk by region ────────────────────────────────────────────────
st.markdown(divider("Behavioral Risk Index by Region"), unsafe_allow_html=True)
st.markdown(
    scale_note(
        "Behavioral Risk Index (BRI): composite score 0.00–1.00. "
        "Formula: 0.35×(Screen/12) + 0.30×Stress + 0.20×(Sleep/10 inverted) + 0.15×(Social/8). "
        "All components normalised to [0,1] before weighting. "
        "0.00 = lowest possible risk · 1.00 = highest possible risk."
    ),
    unsafe_allow_html=True,
)
palette_bri = {"Behavioral_Risk_Index_Recomputed": PALETTE["danger"]}
st.plotly_chart(
    grouped_bar(
        summary,
        "Region_Group",
        ["Behavioral_Risk_Index_Recomputed"],
        palette_bri,
        "Average Behavioral Risk Index by Region",
        y_label="Behavioral Risk Index (0.00 = low · 1.00 = high risk)",
        x_label="Region Group",
    ),
    width="stretch", config=PLOTLY_CONFIG,
)

# ── Insight cards ─────────────────────────────────────────────────────────────
st.markdown(divider("Regional Insights"), unsafe_allow_html=True)
cards = region_insight_cards(dataset)
for card in cards:
    st.markdown(
        insight_chip(f"<strong>{card['title']}.</strong> {card['body']}"),
        unsafe_allow_html=True,
    )
