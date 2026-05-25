"""
pages/4_Behavioral_Archetypes.py

Behavioral Archetypes — KMeans clustering reveals 5 behavioral personas.
All charts carry axis labels and scale notes.
"""
from __future__ import annotations

from src import bootstrap  # noqa: F401

import streamlit as st

from src.charts import cluster_scatter
from src.config import CLUSTER_DESCRIPTIONS, CLUSTER_ICONS, PALETTE
from src.inference import load_artifacts, load_reference_dataset
from src.session import ensure_baseline
from src.styles import (
    apply_styles,
    archetype_card,
    divider,
    hero,
    insight_chip,
    metric_card,
    scale_note,
    score_legend,
    section_header,
)

st.set_page_config(page_title="Behavioral Archetypes — Behavioral Intelligence Advisor", layout="wide")
apply_styles()

PLOTLY_CONFIG = {"responsive": True, "displayModeBar": "hover",
                 "modeBarButtonsToRemove": ["lasso2d", "select2d"]}

try:
    artifacts = load_artifacts()
    reference = load_reference_dataset()
    analysis  = ensure_baseline(artifacts["metadata"], reference)
except Exception as exc:
    st.error(f"⚠️ Could not load models: {exc}. Please reload the Home page first.")
    st.stop()

# ── Hero ─────────────────────────────────────────────────────────────────────
st.markdown(
    hero(
        eyebrow="Page 05 — Behavioral Archetypes",
        title="Behavioral Archetypes.",
        body=(
            "KMeans clustering (K=5) applied to screen time, sleep, social media, notifications, "
            "physical activity, stress, and behavioral risk index across all 16,000 records. "
            "Five distinct behavioral personas emerge from the data."
        ),
    ),
    unsafe_allow_html=True,
)

# ── Your archetype ─────────────────────────────────────────────────────────────
cluster = analysis["cluster"]
st.markdown(
    section_header(
        "Your Behavioral Archetype",
        "Assigned by the trained KMeans model using your current profile.",
    ),
    unsafe_allow_html=True,
)
tone = "danger" if cluster["label"] in {"Burnout Users", "Hyper-Connected Users"} else "default"
st.markdown(
    insight_chip(
        f"<strong>Your archetype: {cluster['label']}.</strong> {cluster['description']}",
        tone=tone,
    ),
    unsafe_allow_html=True,
)
st.markdown(
    insight_chip(
        "<strong>How to change archetypes.</strong> Visit the Scenario Simulation page and "
        "adjust your sleep and screen time — the archetype updates in real time as the model re-assigns you.",
        tone="info",
    ),
    unsafe_allow_html=True,
)

# ── Cluster scatter ────────────────────────────────────────────────────────────
st.markdown(
    section_header(
        "Cluster Constellation — All 16,000 Users",
        "Each dot represents one user, coloured by their assigned archetype. "
        "Axes show Screen Time vs Sleep Hours — the two strongest cluster separators.",
    ),
    unsafe_allow_html=True,
)
st.markdown(
    score_legend([
        ("Burnout Users",            "#EF4444", "High screen, low sleep, elevated stress"),
        ("Hyper-Connected Users",    "#F59E0B", "Very high notifications and social media"),
        ("Sleep-Deprived Achievers", "#8B5CF6", "High work output but chronic sleep deficit"),
        ("Balanced Users",           "#10B981", "Healthy sleep, moderate screen, stable"),
        ("Low-Risk Users",           "#3B82F6", "Light digital use, positive lifestyle indicators"),
    ]),
    unsafe_allow_html=True,
)
st.markdown(
    scale_note(
        "X-axis: Daily screen time (hours, 0–14). "
        "Y-axis: Nightly sleep duration (hours, 2–11). "
        "Green box = healthy benchmark zone (≤6h screen, 7–9h sleep). "
        "Sample: 4,000 randomly selected records from the dataset."
    ),
    unsafe_allow_html=True,
)
st.plotly_chart(
    cluster_scatter(reference),
    width="stretch", config=PLOTLY_CONFIG,
)

# ── Archetype library ──────────────────────────────────────────────────────────
st.markdown(
    section_header(
        "Archetype Library",
        "Five personas derived from K-Means clustering · each has a distinct digital lifestyle fingerprint.",
    ),
    unsafe_allow_html=True,
)
for label, description in CLUSTER_DESCRIPTIONS.items():
    icon = CLUSTER_ICONS.get(label, "??")
    st.markdown(archetype_card(icon, label, description), unsafe_allow_html=True)

# ── Cluster centroids ──────────────────────────────────────────────────────────
st.markdown(divider("Cluster Centroids"), unsafe_allow_html=True)
st.caption(
    "Centroid = the average values of all features for users in that cluster. "
    "Screen time and sleep are in hours/day. Stress and BRI are on a 0.00–1.00 normalised scale."
)

centers   = artifacts["metadata"]["cluster_centers"]
label_map = artifacts["metadata"]["cluster_labels"]

centroid_cols = st.columns(len(centers))
for col, (cluster_id, values) in zip(centroid_cols, centers.items()):
    label = label_map.get(str(cluster_id)) or label_map.get(cluster_id, "Cluster")
    screen = float(values.get("Screen_Time", 0))
    sleep  = float(values.get("Sleep_Hours", 0))
    stress = float(values.get("Stress_Level_Norm", 0))
    bri    = float(values.get("Behavioral_Risk_Index", 0))
    col.markdown(
        metric_card(
            label,
            f"BRI {bri:.2f}",
            delta=f"Screen {screen:.1f}h · Sleep {sleep:.1f}h · Stress {stress:.2f}",
            accent=(
                "danger"    if label == "Burnout Users" else
                "warning"   if label == "Hyper-Connected Users" else
                "purple"    if label == "Sleep-Deprived Achievers" else
                "secondary" if label == "Balanced Users" else
                "primary"
            ),
            scale="BRI 0.00–1.00 · Screen h/day · Sleep h/night · Stress 0.00–1.00",
        ),
        unsafe_allow_html=True,
    )

# ── Methodology note ──────────────────────────────────────────────────────────
st.markdown(
    insight_chip(
        "<strong>Clustering methodology.</strong> KMeans (K=5, n_init=20, random_state=42) fit on "
        "StandardScaler-normalised features: Screen Time, Social Media, Sleep, Notifications, Physical Activity, "
        "Behavioral Risk Index, and Stress Level. "
        "Archetype labels are assigned by inspecting centroid values post-hoc: highest BRI → Burnout, "
        "highest Notifications → Hyper-Connected, lowest Sleep → Sleep-Deprived Achievers, etc.",
        tone="info",
    ),
    unsafe_allow_html=True,
)
