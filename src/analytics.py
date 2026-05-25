from __future__ import annotations

import pandas as pd

from src.config import REGION_GROUPS, USER_TYPES


REGION_METRICS = [
    "Screen_Time",
    "Social_Media_Hours",
    "Sleep_Hours",
    "Stress_Level_Norm",
    "Addiction_Level_Norm",
    "Behavioral_Risk_Index_Recomputed",
    "Notifications_Per_Day",
    "Physical_Activity_Score",
]

USER_METRICS = [
    "Screen_Time",
    "Social_Media_Hours",
    "Sleep_Hours",
    "Stress_Level_Norm",
    "Addiction_Level_Norm",
    "Behavioral_Risk_Index_Recomputed",
    "Notifications_Per_Day",
    "Physical_Activity_Score",
    "Work_Study_Hours",
]


def region_summary(dataset: pd.DataFrame) -> pd.DataFrame:
    return (
        dataset.groupby("Region_Group")[REGION_METRICS]
        .mean()
        .reindex(REGION_GROUPS)
        .reset_index()
    )


def user_summary(dataset: pd.DataFrame) -> pd.DataFrame:
    return (
        dataset.groupby("User_Type")[USER_METRICS]
        .mean()
        .reindex(USER_TYPES)
        .reset_index()
    )


def addiction_distribution(dataset: pd.DataFrame, by: str) -> pd.DataFrame:
    counts = (
        dataset.groupby([by, "Addiction_Category"])
        .size()
        .reset_index(name="count")
    )
    totals = counts.groupby(by)["count"].transform("sum")
    counts["share"] = (counts["count"] / totals * 100.0).round(1)
    return counts


def burnout_share(dataset: pd.DataFrame, by: str) -> pd.DataFrame:
    high_stress = dataset.assign(is_burnout=(dataset["Stress_Level_Norm"] > 0.4).astype(int))
    return (
        high_stress.groupby(by)["is_burnout"]
        .mean()
        .reset_index(name="burnout_share")
    )


def sleep_deficit_share(dataset: pd.DataFrame, by: str, threshold: float = 6.0) -> pd.DataFrame:
    deficit = dataset.assign(is_deficit=(dataset["Sleep_Hours"] < threshold).astype(int))
    return (
        deficit.groupby(by)["is_deficit"]
        .mean()
        .reset_index(name="deficit_share")
    )


def region_insight_cards(dataset: pd.DataFrame) -> list[dict[str, str]]:
    summary = region_summary(dataset).set_index("Region_Group")
    cards: list[dict[str, str]] = []

    if {"India", "Global"}.issubset(summary.index):
        screen_delta = summary.loc["India", "Screen_Time"] - summary.loc["Global", "Screen_Time"]
        if abs(screen_delta) > 0.2:
            direction = "higher" if screen_delta > 0 else "lower"
            cards.append({
                "title": "India vs Global",
                "body": f"India users show {abs(screen_delta):.1f}h {direction} screen time than the global average.",
            })

    if {"USA", "Global"}.issubset(summary.index):
        sleep_delta = summary.loc["USA", "Sleep_Hours"] - summary.loc["Global", "Sleep_Hours"]
        if abs(sleep_delta) > 0.1:
            direction = "more" if sleep_delta > 0 else "less"
            cards.append({
                "title": "USA Sleep Pattern",
                "body": f"USA users sleep {abs(sleep_delta):.1f}h {direction} per night than the global average.",
            })

    if "USA" in summary.index:
        notif_value = summary.loc["USA", "Notifications_Per_Day"]
        cards.append({
            "title": "USA Notification Load",
            "body": f"USA users average {notif_value:.0f} notifications/day — a strong digital fatigue input.",
        })

    if "India" in summary.index:
        social = summary.loc["India", "Social_Media_Hours"]
        cards.append({
            "title": "India Social Media",
            "body": f"India users spend {social:.1f}h/day on social media on average.",
        })

    if not cards:
        cards.append({
            "title": "Cohort Spread",
            "body": "Regional cohort signals are tightly clustered around the global baseline.",
        })
    return cards[:4]


def user_insight_cards(dataset: pd.DataFrame) -> list[dict[str, str]]:
    summary = user_summary(dataset).set_index("User_Type")
    cards: list[dict[str, str]] = []
    if {"Student", "Professional"}.issubset(summary.index):
        screen_delta = (
            summary.loc["Student", "Screen_Time"]
            - summary.loc["Professional", "Screen_Time"]
        )
        direction = "more" if screen_delta > 0 else "less"
        cards.append({
            "title": "Students vs Professionals: Screen",
            "body": f"Students spend {abs(screen_delta):.1f}h {direction} on screens than professionals.",
        })
        sleep_delta = (
            summary.loc["Student", "Sleep_Hours"]
            - summary.loc["Professional", "Sleep_Hours"]
        )
        direction = "more" if sleep_delta > 0 else "less"
        cards.append({
            "title": "Sleep Comparison",
            "body": f"Students sleep {abs(sleep_delta):.1f}h {direction} per night than professionals.",
        })
        risk_delta = (
            summary.loc["Student", "Behavioral_Risk_Index_Recomputed"]
            - summary.loc["Professional", "Behavioral_Risk_Index_Recomputed"]
        )
        winner = "Students" if risk_delta > 0 else "Professionals"
        cards.append({
            "title": "Behavioral Risk Index",
            "body": f"{winner} carry a slightly higher recomputed BRI — by {abs(risk_delta):.2f}.",
        })
    if not cards:
        cards.append({
            "title": "Segment Spread",
            "body": "Student and Professional baselines are tightly aligned in this cohort.",
        })
    return cards[:4]
