"""
charts.py — All Plotly chart builders for the Behavioral Intelligence Advisor.

Every chart includes:
  • Properly labelled X and Y axes with units
  • Scale/range annotations so non-technical readers understand what scores mean
  • Hover templates with plain-English descriptions
  • Consistent flat design (no shadows, no gradients)
"""
from __future__ import annotations

from typing import Iterable

import pandas as pd
import plotly.graph_objects as go

from src.config import (
    ADDICTION_PALETTE,
    PALETTE,
    REGION_PALETTE,
    USER_PALETTE,
    UI_FIELD_LABELS,
)


FONT = "Inter, Plus Jakarta Sans, ui-sans-serif, system-ui, sans-serif"

# ── Axis label style helper ─────────────────────────────────────────────────

def _axis(title: str, *, suffix: str = "", fmt: str = "", range_: list | None = None) -> dict:
    """Return a consistent axis dict with title styling."""
    d: dict = dict(
        title=dict(
            text=title,
            font=dict(size=12, color=PALETTE["soft_text"], family=FONT),
            standoff=10,
        ),
        tickfont=dict(size=11, color=PALETTE["soft_text"], family=FONT),
        showgrid=True,
        gridcolor=PALETTE["border"],
        gridwidth=1,
        zerolinecolor=PALETTE["border"],
        linecolor=PALETTE["border"],
    )
    if suffix:
        d["ticksuffix"] = suffix
    if fmt:
        d["tickformat"] = fmt
    if range_:
        d["range"] = range_
    return d


# ── Base layout ─────────────────────────────────────────────────────────────

def _flat_layout(
    fig: go.Figure,
    height: int = 320,
    *,
    has_legend: bool = False,
    has_title: bool = True,
    left_margin: int = 72,
) -> go.Figure:
    top_margin = 64 if has_title else 28
    bottom_margin = 88 if has_legend else 42
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=PALETTE["background"],
        font=dict(family=FONT, color=PALETTE["foreground"], size=13),
        margin=dict(l=left_margin, r=24, t=top_margin, b=bottom_margin),
        height=height + (44 if has_legend else 0),
        autosize=True,
        hoverlabel=dict(
            bgcolor="rgba(13,20,36,0.96)",
            font=dict(color=PALETTE["foreground"], family=FONT, size=12),
            bordercolor="rgba(255,255,255,0.15)",
        ),
    )
    if has_legend:
        fig.update_layout(
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.20,
                xanchor="center",
                x=0.5,
                font=dict(size=12, family=FONT),
                bgcolor="rgba(0,0,0,0)",
                borderwidth=0,
            )
        )
    return fig


def _title(text: str, subtitle: str = "") -> dict:
    full = f"<b>{text}</b>"
    if subtitle:
        full += f"<br><span style='font-size:11px;color:{PALETTE['soft_text']}'>{subtitle}</span>"
    return dict(
        text=full,
        font=dict(size=15, color=PALETTE["foreground"], family=FONT),
        x=0.0,
        xanchor="left",
        y=0.99,
        yanchor="top",
        pad=dict(b=6),
    )


# ── Gauge ───────────────────────────────────────────────────────────────────

def gauge(
    title: str,
    value: float,
    minimum: float,
    maximum: float,
    accent: str,
    *,
    scale_label: str = "Scale: 0.00 = lowest  ·  1.00 = highest",
) -> go.Figure:
    """
    Semi-circular gauge with colour-coded risk zones and a readable scale note.

    Zone colours:
      0.00 – 0.33  →  green   (Low)
      0.33 – 0.66  →  amber   (Moderate)
      0.66 – 1.00  →  red     (High)
    """
    span = maximum - minimum
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=value,
            number=dict(
                font=dict(size=40, color=PALETTE["foreground"], family=FONT),
                valueformat=".2f",
                suffix="",
            ),
            gauge=dict(
                axis=dict(
                    range=[minimum, maximum],
                    tickcolor=PALETTE["soft_text"],
                    tickfont=dict(size=10, family=FONT),
                    nticks=6,
                ),
                bar=dict(color=accent, thickness=0.28),
                bgcolor=PALETTE["muted"],
                borderwidth=0,
                steps=[
                    dict(range=[minimum, minimum + span * 0.33], color="rgba(16,185,129,0.18)"),
                    dict(range=[minimum + span * 0.33, minimum + span * 0.66], color="rgba(245,158,11,0.16)"),
                    dict(range=[minimum + span * 0.66, maximum], color="rgba(239,68,68,0.18)"),
                ],
                threshold=dict(
                    line=dict(color="rgba(255,255,255,0.60)", width=2),
                    thickness=0.78,
                    value=value,
                ),
            ),
            domain={"x": [0, 1], "y": [0.08, 1]},
            title=dict(
                text=f"<b>{title}</b><br><span style='font-size:10px;color:{PALETTE['soft_text']}'>{scale_label}</span>",
                font=dict(size=13, color=PALETTE["soft_text"], family=FONT),
            ),
        )
    )
    fig.update_layout(
        transition=dict(duration=600, easing="cubic-in-out"),
    )
    return _flat_layout(fig, height=260, has_legend=False, has_title=False)


# ── Donut ───────────────────────────────────────────────────────────────────

def donut(
    title: str,
    labels: Iterable[str],
    values: Iterable[float],
    colors: Iterable[str],
) -> go.Figure:
    """Donut chart with percentage labels. Values can be raw counts or percentages."""
    fig = go.Figure(
        go.Pie(
            labels=list(labels),
            values=list(values),
            hole=0.62,
            marker=dict(colors=list(colors), line=dict(color=PALETTE["background"], width=2)),
            textinfo="label+percent",
            textfont=dict(family=FONT, color=PALETTE["foreground"], size=12),
            hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Share: %{percent}<extra></extra>",
        )
    )
    fig.update_layout(title=_title(title, "Share of each category in the selected group"))
    return _flat_layout(fig, height=320, has_legend=True)


# ── Grouped bar ──────────────────────────────────────────────────────────────

def grouped_bar(
    frame: pd.DataFrame,
    category: str,
    metrics: list[str],
    palette: dict[str, str],
    title: str,
    *,
    y_label: str = "Average value",
    x_label: str = "Group",
    y_suffix: str = "",
) -> go.Figure:
    """
    Grouped bar chart.
    Each bar shows a dataset mean.  Hover shows the precise value.
    """
    fig = go.Figure()
    for metric in metrics:
        human = UI_FIELD_LABELS.get(metric, metric)
        y_vals = frame[metric].astype(float).tolist()
        fig.add_bar(
            x=frame[category].astype(str).tolist(),
            y=y_vals,
            name=human,
            marker_color=palette.get(metric, PALETTE["primary"]),
            text=[f"{v:.2f}" for v in y_vals],
            textposition="outside",
            textfont=dict(size=11, family=FONT),
            hovertemplate=f"<b>%{{x}}</b><br>{human}: %{{y:.2f}}{y_suffix}<extra></extra>",
        )
    fig.update_layout(
        barmode="group",
        title=_title(title, "Dataset means per group · Hover for exact values"),
        xaxis=_axis(x_label),
        yaxis=_axis(y_label, suffix=y_suffix),
        bargap=0.22,
        bargroupgap=0.06,
    )
    return _flat_layout(fig, height=400, has_legend=True)


# ── Stacked share ────────────────────────────────────────────────────────────

def stacked_share(
    frame: pd.DataFrame,
    category: str,
    value: str,
    group: str,
    palette: dict[str, str],
    title: str,
    *,
    y_label: str = "Share of group (%)",
    x_label: str = "Group",
) -> go.Figure:
    """100 % stacked bar — shows composition within each group."""
    fig = go.Figure()
    for level in frame[group].unique().tolist():
        sub = frame[frame[group] == level]
        fig.add_bar(
            x=sub[category].astype(str).tolist(),
            y=sub[value].astype(float).tolist(),
            name=str(level),
            marker_color=palette.get(level, PALETTE["primary"]),
            text=[f"{v:.1f}%" for v in sub[value].astype(float)],
            textposition="inside",
            textfont=dict(size=11, family=FONT, color="#FFFFFF"),
            hovertemplate=f"<b>%{{x}}</b><br>{level}: %{{y:.1f}}%<extra></extra>",
        )
    fig.update_layout(
        barmode="stack",
        title=_title(title, "Each bar sums to 100% — shows proportion of each category"),
        xaxis=_axis(x_label),
        yaxis=_axis(y_label, suffix="%", range_=[0, 105]),
    )
    return _flat_layout(fig, height=400, has_legend=True)


# ── Violin by region ─────────────────────────────────────────────────────────

_METRIC_UNITS: dict[str, str] = {
    "Stress_Level_Norm":           "Normalised stress score (0.00 = calm · 1.00 = extreme stress)",
    "Notifications_Per_Day":       "Notifications received per day",
    "Sleep_Hours":                 "Hours of sleep per night",
    "Screen_Time":                 "Hours of screen use per day",
    "Social_Media_Hours":          "Hours on social media per day",
    "Addiction_Level_Norm":        "Addiction severity score (0.00 = none · 1.00 = severe)",
    "Behavioral_Risk_Index_Recomputed": "Behavioral Risk Index (0.00 = low risk · 1.00 = high risk)",
    "Physical_Activity_Score":     "Physical activity score (1 = inactive · 5 = very active)",
}


def violin_by_region(dataset: pd.DataFrame, metric: str, title: str) -> go.Figure:
    """
    Violin plot — shows the full distribution (not just the mean) per region.
    The embedded box shows the interquartile range; the centre line is the median.
    """
    y_label = _METRIC_UNITS.get(metric, UI_FIELD_LABELS.get(metric, metric))
    fig = go.Figure()
    for region, color in REGION_PALETTE.items():
        subset = dataset[dataset["Region_Group"] == region]
        if subset.empty:
            continue
        fig.add_trace(
            go.Violin(
                x=[region] * len(subset),
                y=subset[metric].astype(float),
                name=region,
                line_color=color,
                fillcolor=color,
                opacity=0.50,
                box_visible=True,
                meanline_visible=True,
                meanline=dict(color=PALETTE["foreground"], width=2),
                hoverinfo="y+name",
                hovertemplate=f"<b>{region}</b><br>Value: %{{y:.2f}}<extra></extra>",
            )
        )
    fig.update_layout(
        title=_title(title, "Width shows density · inner box = IQR · centre line = median"),
        xaxis=_axis("Region Group"),
        yaxis=_axis(y_label),
        showlegend=False,
    )
    return _flat_layout(fig, height=400, has_legend=False, left_margin=90)


# ── Correlation heatmap ───────────────────────────────────────────────────────

def correlation_heatmap(dataset: pd.DataFrame, columns: list[str]) -> go.Figure:
    """
    Pearson correlation matrix.
    Reading guide:
      +1.0  = perfect positive relationship
       0.0  = no linear relationship
      -1.0  = perfect negative relationship
    """
    matrix = dataset[columns].corr().round(2)
    human_labels = [UI_FIELD_LABELS.get(c, c) for c in columns]
    fig = go.Figure(
        go.Heatmap(
            z=matrix.values,
            x=human_labels,
            y=human_labels,
            colorscale=[
                (0.0, PALETTE["primary"]),
                (0.5, PALETTE["background"]),
                (1.0, PALETTE["accent"]),
            ],
            zmid=0,
            zmin=-1,
            zmax=1,
            text=matrix.values,
            texttemplate="<b>%{text:.2f}</b>",
            textfont=dict(size=10, family=FONT),
            colorbar=dict(
                thickness=14,
                tickvals=[-1, -0.5, 0, 0.5, 1],
                ticktext=["-1.0<br>Negative", "-0.5", "0<br>None", "+0.5", "+1.0<br>Positive"],
                tickfont=dict(size=10, family=FONT),
                title=dict(text="Pearson r", font=dict(size=11, family=FONT)),
            ),
            hovertemplate="<b>%{y}</b> vs <b>%{x}</b><br>Correlation: %{z:.2f}<extra></extra>",
        )
    )
    fig.update_layout(
        title=_title(
            "Behavioral Correlation Map",
            "+1.0 = strong positive link  ·  0 = no relationship  ·  −1.0 = strong inverse link",
        ),
        xaxis=dict(
            tickfont=dict(size=10, family=FONT),
            tickangle=-35,
            linecolor=PALETTE["border"],
        ),
        yaxis=dict(
            tickfont=dict(size=10, family=FONT),
            linecolor=PALETTE["border"],
            autorange="reversed",
        ),
    )
    return _flat_layout(fig, height=560, has_legend=False, left_margin=120)


# ── Feature importance bar ────────────────────────────────────────────────────

def feature_importance_bar(importances: dict[str, float], target: str) -> go.Figure:
    """
    Horizontal bar chart of RandomForest Mean Decrease Impurity (MDI) importance.

    Scale: 0.00 – 1.00 (all bars sum to 1.00)
    A bar of 0.30 means that feature explains ~30% of the model's decision weight.
    """
    items = list(importances.items())[:8]
    labels = [UI_FIELD_LABELS.get(name, name) for name, _ in items][::-1]
    values = [v for _, v in items][::-1]

    color_map = {
        "stress": PALETTE["primary"],
        "addiction": PALETTE["accent"],
        "productivity": PALETTE["secondary"],
    }
    bar_color = color_map.get(target, PALETTE["primary"])

    fig = go.Figure(
        go.Bar(
            x=values,
            y=labels,
            orientation="h",
            marker_color=bar_color,
            marker_line_width=0,
            text=[f"{v:.1%}" for v in values],
            textposition="outside",
            textfont=dict(size=11, family=FONT),
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Importance: %{x:.1%}<br>"
                "<i>Higher = more influential in this model</i><extra></extra>"
            ),
        )
    )
    fig.update_layout(
        title=_title(
            f"Feature Importance — {target.title()} Model",
            "Mean Decrease Impurity · bars sum to 100% · higher = more influence on predictions",
        ),
        xaxis=_axis(
            "Relative Importance (share of model weight, 0.0–1.0)",
            fmt=".0%",
            range_=[0, max(values) * 1.28 if values else 1.0],
        ),
        yaxis=_axis("Input Feature"),
    )
    return _flat_layout(fig, height=420, has_legend=False, left_margin=140)


# ── Local impact / sensitivity chart ─────────────────────────────────────────

def local_impact_chart(impacts: dict[str, dict[str, float]], target: str) -> go.Figure:
    """
    Perturbation sensitivity: each feature is nudged by a fixed positive delta;
    the bar shows the resulting change in the model's output for *your* profile.

    X-axis interpretation:
      Positive (red)  → nudging this feature UP increases the risk score
      Negative (green)→ nudging this feature UP decreases the risk score (i.e., it's protective)
    """
    rows = sorted(impacts.items(), key=lambda item: abs(item[1].get(target, 0.0)), reverse=True)
    labels = [UI_FIELD_LABELS.get(name, name) for name, _ in rows][::-1]
    values = [item[1].get(target, 0.0) for item in rows][::-1]
    colors = [PALETTE["danger"] if v > 0 else PALETTE["secondary"] for v in values]

    target_names = {"stress": "stress score", "addiction": "addiction severity", "productivity": "productivity score"}
    target_label = target_names.get(target, target)

    fig = go.Figure(
        go.Bar(
            x=values,
            y=labels,
            orientation="h",
            marker_color=colors,
            marker_line_width=0,
            text=[f"{v:+.3f}" for v in values],
            textposition="outside",
            textfont=dict(size=11, family=FONT),
            hovertemplate=(
                "<b>%{y}</b><br>"
                f"Predicted change in {target_label}: %{{x:+.3f}}<br>"
                "<i>Red = raises risk · Green = lowers risk</i><extra></extra>"
            ),
        )
    )
    # Zero reference line
    fig.add_vline(x=0, line_color=PALETTE["foreground"], line_width=1.5, line_dash="solid")

    fig.update_layout(
        title=_title(
            f"Local Sensitivity — {target.title()}",
            f"Effect of nudging each feature up · Red = raises {target_label} · Green = lowers it",
        ),
        xaxis=_axis(
            f"Predicted change in {target_label} (model output units)",
        ),
        yaxis=_axis("Lifestyle Feature"),
    )
    return _flat_layout(fig, height=420, has_legend=False, left_margin=150)


# ── Radar chart ───────────────────────────────────────────────────────────────

def radar_chart(payload: dict[str, list[float]]) -> go.Figure:
    """
    Lifestyle Balance radar comparing the user's profile to the cohort average.

    Scale: 0 = worst possible lifestyle outcome · 100 = optimal outcome
    All axes are oriented so that OUTER is BETTER (stress is inverted).
    """
    axes = payload["axes"]
    fig = go.Figure()
    fig.add_trace(
        go.Scatterpolar(
            r=payload["user"] + [payload["user"][0]],
            theta=axes + [axes[0]],
            fill="toself",
            name="Your Profile",
            line=dict(color=PALETTE["primary"], width=3),
            fillcolor="rgba(59,130,246,0.15)",
            hovertemplate="<b>%{theta}</b><br>Your score: %{r:.0f}/100<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatterpolar(
            r=payload["average"] + [payload["average"][0]],
            theta=axes + [axes[0]],
            fill="toself",
            name="Cohort Average",
            line=dict(color=PALETTE["accent"], width=2, dash="dot"),
            fillcolor="rgba(245,158,11,0.08)",
            hovertemplate="<b>%{theta}</b><br>Cohort average: %{r:.0f}/100<extra></extra>",
        )
    )
    fig.update_layout(
        polar=dict(
            bgcolor=PALETTE["background"],
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                gridcolor=PALETTE["border"],
                tickfont=dict(size=9, family=FONT),
                ticksuffix="",
                tickvals=[0, 25, 50, 75, 100],
                ticktext=["0", "25", "50", "75", "100"],
            ),
            angularaxis=dict(
                gridcolor=PALETTE["border"],
                tickfont=dict(size=11, family=FONT, color=PALETTE["foreground"]),
            ),
        ),
        title=_title(
            "Lifestyle Balance vs Cohort",
            "Score 0–100 · Outer edge = best outcome · All axes: HIGHER is BETTER",
        ),
    )
    return _flat_layout(fig, height=460, has_legend=True)


# ── Percentile chart ──────────────────────────────────────────────────────────

def percentile_chart(percentiles: dict[str, float]) -> go.Figure:
    """
    Where the user sits relative to the full 16,000-record cohort.

    Scale:
      0th  = lower than everyone in the dataset
      50th = exactly average
      100th= higher than everyone in the dataset
    For stress / screen time a HIGH percentile is a WARNING.
    For sleep / activity a HIGH percentile is GOOD.
    """
    labels = [UI_FIELD_LABELS.get(k, k) for k in percentiles.keys()]
    values = list(percentiles.values())
    colors = [
        PALETTE["danger"] if v >= 75 else PALETTE["accent"] if v >= 50 else PALETTE["secondary"]
        for v in values
    ]
    fig = go.Figure(
        go.Bar(
            x=values,
            y=labels,
            orientation="h",
            marker_color=colors,
            marker_line_width=0,
            text=[f"{v:.0f}th" for v in values],
            textposition="outside",
            textfont=dict(size=11, family=FONT),
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Percentile: %{x:.0f}th<br>"
                "<i>50th = average · >75th = high vs peers</i><extra></extra>"
            ),
        )
    )
    # Average reference line
    fig.add_vline(x=50, line_dash="dash", line_color=PALETTE["soft_text"], line_width=1.5,
                  annotation_text="Cohort avg", annotation_font_size=10,
                  annotation_font_color=PALETTE["soft_text"],
                  annotation_position="top right")
    fig.update_layout(
        title=_title(
            "Where You Sit vs Cohort (Percentile Rank)",
            "0th = lowest · 50th = average · 100th = highest · Dashed line = cohort mean",
        ),
        xaxis=_axis("Cohort Percentile Rank (0–100)", range_=[0, 115]),
        yaxis=_axis("Lifestyle Feature"),
    )
    return _flat_layout(fig, height=360, has_legend=False, left_margin=150)


# ── Before / After comparison ─────────────────────────────────────────────────

def before_after_chart(baseline: dict[str, object], scenario: dict[str, object]) -> go.Figure:
    """
    Side-by-side bars comparing current vs simulated profile.

    All values converted to a 0–100 scale for consistent visual comparison.

    Direction notes (shown in chart subtitle):
      Stress / Addiction / BRI  → LOWER is better
      Productivity / Lifestyle  → HIGHER is better
    """
    metrics = ["Stress", "Addiction Severity", "Productivity", "BRI", "Lifestyle Score"]
    directions = ["↓ lower = better", "↓ lower = better", "↑ higher = better",
                  "↓ lower = better", "↑ higher = better"]

    base_vals = [
        baseline["stress_level"] * 100,
        baseline["addiction"]["severity"] * 100,
        baseline["productivity"]["productivity_score"] * 100,
        baseline["behavioral_risk_index"] * 100,
        baseline["lifestyle_score"]["total"],
    ]
    sim_vals = [
        scenario["stress_level"] * 100,
        scenario["addiction"]["severity"] * 100,
        scenario["productivity"]["productivity_score"] * 100,
        scenario["behavioral_risk_index"] * 100,
        scenario["lifestyle_score"]["total"],
    ]
    x_labels = [f"{m}<br><span style='font-size:9px;color:#6B7280'>{d}</span>"
                 for m, d in zip(metrics, directions)]

    fig = go.Figure()
    fig.add_bar(
        x=x_labels,
        y=base_vals,
        name="Current Profile",
        marker_color=PALETTE["accent"],
        marker_line_width=0,
        text=[f"{v:.0f}" for v in base_vals],
        textposition="outside",
        textfont=dict(size=11, family=FONT),
        hovertemplate="<b>%{x}</b><br>Current: %{y:.1f}/100<extra></extra>",
    )
    fig.add_bar(
        x=x_labels,
        y=sim_vals,
        name="Simulated Scenario",
        marker_color=PALETTE["primary"],
        marker_line_width=0,
        text=[f"{v:.0f}" for v in sim_vals],
        textposition="outside",
        textfont=dict(size=11, family=FONT),
        hovertemplate="<b>%{x}</b><br>Simulated: %{y:.1f}/100<extra></extra>",
    )
    fig.update_layout(
        barmode="group",
        title=_title(
            "Scenario: Before vs After",
            "All scores on a 0–100 scale · ↓ lower is better for risk metrics · ↑ higher is better for outputs",
        ),
        xaxis=_axis("Metric (with direction note)"),
        yaxis=_axis("Score (0–100 unified scale)", range_=[0, 118]),
        bargap=0.22,
        bargroupgap=0.06,
    )
    return _flat_layout(fig, height=420, has_legend=True)


# ── Cluster scatter ───────────────────────────────────────────────────────────

_CLUSTER_COLORS = {
    "Burnout Users":           "#EF4444",
    "Hyper-Connected Users":   "#F59E0B",
    "Sleep-Deprived Achievers":"#8B5CF6",
    "Balanced Users":          "#10B981",
    "Low-Risk Users":          "#3B82F6",
}


def cluster_scatter(dataset: pd.DataFrame, sample_size: int = 4000) -> go.Figure:
    """
    Scatter plot — each point is one user, coloured by behavioural archetype.

    X-axis: Screen Time (h/day) — 0 to ~14 h
    Y-axis: Sleep Hours per night — 2 to ~11 h

    Reading: Burnout Users (red) typically appear top-right (high screen, low sleep).
    Balanced Users (green) cluster bottom-left (moderate screen, healthy sleep).
    """
    frame = dataset.sample(min(sample_size, len(dataset)), random_state=42)
    fig = go.Figure()
    for label in ["Burnout Users", "Hyper-Connected Users", "Sleep-Deprived Achievers",
                   "Balanced Users", "Low-Risk Users"]:
        subset = frame[frame["Cluster_Label"] == label]
        if subset.empty:
            continue
        fig.add_trace(
            go.Scatter(
                x=subset["Screen_Time"],
                y=subset["Sleep_Hours"],
                mode="markers",
                name=label,
                marker=dict(
                    size=6,
                    opacity=0.55,
                    color=_CLUSTER_COLORS.get(label, PALETTE["primary"]),
                    line=dict(width=0),
                ),
                hovertemplate=(
                    f"<b>{label}</b><br>"
                    "Screen Time: %{x:.1f} h/day<br>"
                    "Sleep: %{y:.1f} h/night<extra></extra>"
                ),
            )
        )

    # Healthy zone reference box
    fig.add_shape(
        type="rect", x0=0, x1=6, y0=7, y1=9,
        fillcolor="rgba(16,185,129,0.07)",
        line=dict(color=PALETTE["secondary"], width=1, dash="dot"),
    )
    fig.add_annotation(
        x=3, y=8, text="Healthy zone<br>(≤6h screen · 7–9h sleep)",
        showarrow=False,
        font=dict(size=9, color=PALETTE["secondary"], family=FONT),
        align="center",
    )

    fig.update_layout(
        title=_title(
            "Cluster Constellation — Screen Time vs Sleep",
            "Each dot = one user · Colour = behavioural archetype · Green box = healthy benchmark zone",
        ),
        xaxis=_axis(
            "Daily Screen Time (hours)",
            range_=[-0.5, 15],
        ),
        yaxis=_axis(
            "Nightly Sleep Duration (hours)",
            range_=[1.5, 12],
        ),
    )
    return _flat_layout(fig, height=520, has_legend=True, left_margin=64)


# ── Addiction distribution chart ──────────────────────────────────────────────

def addiction_distribution_chart(frame: pd.DataFrame, category: str, title: str) -> go.Figure:
    """
    100% stacked bar showing the split of Low / Moderate / High addiction
    within each group (region or user type).
    """
    fig = go.Figure()
    for level in ["Low", "Moderate", "High"]:
        sub = frame[frame["Addiction_Category"] == level]
        if sub.empty:
            continue
        fig.add_bar(
            x=sub[category].astype(str).tolist(),
            y=sub["share"].astype(float).tolist(),
            name=level,
            marker_color=ADDICTION_PALETTE.get(level, PALETTE["primary"]),
            marker_line_width=0,
            text=[f"{v:.1f}%" for v in sub["share"].astype(float)],
            textposition="inside",
            textfont=dict(size=11, family=FONT, color="#FFFFFF"),
            hovertemplate=(
                f"<b>%{{x}}</b><br>"
                f"Addiction level: {level}<br>"
                "Share: %{y:.1f}%<extra></extra>"
            ),
        )
    fig.update_layout(
        barmode="stack",
        title=_title(
            title,
            "Low = minimal digital dependency · Moderate = watch-list · High = intervention recommended",
        ),
        xaxis=_axis("Group"),
        yaxis=_axis("Proportion within group (%)", suffix="%", range_=[0, 105]),
    )
    return _flat_layout(fig, height=420, has_legend=True)


# ── User-type grouped bar ─────────────────────────────────────────────────────

def user_grouped_bar(
    frame: pd.DataFrame,
    metrics: list[str],
    title: str,
    *,
    y_label: str = "Average value",
) -> go.Figure:
    """Grouped bar comparing Student vs Professional vs Mixed on selected metrics."""
    fig = go.Figure()
    for metric in metrics:
        human = UI_FIELD_LABELS.get(metric, metric)
        fig.add_bar(
            x=frame["User_Type"].astype(str).tolist(),
            y=frame[metric].astype(float).tolist(),
            name=human,
            marker_color=USER_PALETTE.get(frame["User_Type"].iloc[0] if not frame.empty else "Student",
                                           PALETTE["primary"]),
            text=[f"{v:.2f}" for v in frame[metric].astype(float)],
            textposition="outside",
            textfont=dict(size=11, family=FONT),
            hovertemplate=f"<b>%{{x}}</b><br>{human}: %{{y:.2f}}<extra></extra>",
        )
    fig.update_layout(
        barmode="group",
        title=_title(title, "Dataset means per user type · Hover for exact values"),
        xaxis=_axis("User Type"),
        yaxis=_axis(y_label),
        bargap=0.22,
        bargroupgap=0.06,
    )
    return _flat_layout(fig, height=400, has_legend=True)


# ── Choropleth Risk Map ──────────────────────────────────────────────────────

def choropleth_risk_map(summary: "pd.DataFrame") -> go.Figure:
    """World choropleth — Behavioral Risk Index for India, USA, and Global cohorts."""

    ISO_MAP  = {"India": "IND", "USA": "USA"}

    z_col      = "Behavioral_Risk_Index_Recomputed"
    stress_col = "Stress_Level_Norm"
    sleep_col  = "Sleep_Hours"
    screen_col = "Screen_Time"
    social_col = "Social_Media_Hours"
    addict_col = "Addiction_Level_Norm"

    locations, z_vals, hover_texts = [], [], []

    for _, row in summary.iterrows():
        rg = row["Region_Group"]
        if rg not in ISO_MAP:
            continue
        locations.append(ISO_MAP[rg])
        bri = float(row.get(z_col, 0))
        z_vals.append(bri)
        hover_texts.append(
            f"<b>{rg} Cohort</b><br>"
            f"━━━━━━━━━━━━━━━━━━━━<br>"
            f"Behavioral Risk Index: <b>{bri:.3f}</b><br>"
            f"Stress Level (norm 0\u20131): <b>{float(row.get(stress_col, 0)):.3f}</b><br>"
            f"Avg Sleep: <b>{float(row.get(sleep_col, 0)):.1f} h/night</b><br>"
            f"Avg Screen Time: <b>{float(row.get(screen_col, 0)):.1f} h/day</b><br>"
            f"Avg Social Media: <b>{float(row.get(social_col, 0)):.1f} h/day</b><br>"
            f"Addiction Level (norm): <b>{float(row.get(addict_col, 0)):.3f}</b>"
        )

    global_rows = summary[summary["Region_Group"] == "Global"]
    global_bri  = float(global_rows[z_col].values[0]) if not global_rows.empty else None
    global_stress = float(global_rows[stress_col].values[0]) if not global_rows.empty else None
    global_sleep  = float(global_rows[sleep_col].values[0])  if not global_rows.empty else None
    global_screen = float(global_rows[screen_col].values[0]) if not global_rows.empty else None

    fig = go.Figure()

    fig.add_trace(go.Choropleth(
        locations=locations,
        z=z_vals,
        text=hover_texts,
        hoverinfo="text",
        locationmode="ISO-3",
        colorscale=[
            [0.00, "#059669"],
            [0.35, "#10B981"],
            [0.55, "#F59E0B"],
            [0.78, "#FB923C"],
            [1.00, "#EF4444"],
        ],
        zmin=0,
        zmax=1,
        marker=dict(line=dict(color="rgba(255,255,255,0.18)", width=1.2)),
        colorbar=dict(
            title=dict(
                text="Behavioral Risk Index",
                font=dict(color=PALETTE["soft_text"], size=11, family=FONT),
                side="right",
            ),
            tickfont=dict(color=PALETTE["soft_text"], size=10, family=FONT),
            tickformat=".2f",
            bgcolor="rgba(0,0,0,0)",
            borderwidth=0,
            thickness=12,
            len=0.55,
            x=1.01,
        ),
        name="",
    ))

    annotations = [
        dict(x=78,  y=22,  text="<b>India</b>",  xanchor="center", yanchor="middle",
             showarrow=False, font=dict(color="#FCD34D", size=11, family=FONT),
             bgcolor="rgba(0,0,0,0.55)", borderpad=3),
        dict(x=-98, y=38,  text="<b>USA</b>",     xanchor="center", yanchor="middle",
             showarrow=False, font=dict(color="#A5B4FC", size=11, family=FONT),
             bgcolor="rgba(0,0,0,0.55)", borderpad=3),
    ]
    if global_bri is not None:
        txt = (
            f"<b>Global Cohort</b><br>"
            f"BRI: {global_bri:.3f}<br>"
            f"Stress: {global_stress:.3f}<br>"
            f"Sleep: {global_sleep:.1f} h<br>"
            f"Screen: {global_screen:.1f} h"
        )
        annotations.append(dict(
            x=20, y=-20,
            text=txt,
            xanchor="center", yanchor="middle", showarrow=False,
            font=dict(color="#6EE7B7", size=10, family=FONT),
            bgcolor="rgba(13,20,36,0.82)", borderpad=5,
            bordercolor="rgba(16,185,129,0.45)", borderwidth=1,
        ))

    fig.update_layout(
        geo=dict(
            showframe=False,
            showcoastlines=True,
            coastlinecolor="rgba(255,255,255,0.10)",
            showland=True,
            landcolor="#131E30",
            showocean=True,
            oceancolor="#070C18",
            showcountries=True,
            countrycolor="rgba(255,255,255,0.07)",
            showlakes=False,
            bgcolor="rgba(0,0,0,0)",
            projection=dict(type="natural earth"),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT, color=PALETTE["foreground"], size=12),
        margin=dict(l=0, r=0, t=44, b=0),
        height=440,
        annotations=annotations,
        hoverlabel=dict(
            bgcolor="rgba(13,20,36,0.96)",
            font=dict(color=PALETTE["foreground"], family=FONT, size=12),
            bordercolor="rgba(255,255,255,0.15)",
        ),
    )
    return fig
