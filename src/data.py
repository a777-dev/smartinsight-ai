from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from src.config import (
    BRI_WEIGHTS,
    PROCESSED_DATA_PATH,
    RAW_DATA_PATH,
)

import numpy as np
import pandas as pd


NUMERIC_COLUMNS_RAW = [
    "Age",
    "Screen_Time",
    "Social_Media_Hours",
    "Gaming_Hours",
    "Work_Study_Hours",
    "Sleep_Hours",
    "Stress_Level",
    "Anxiety_Level",
    "Depression_Level",
    "Notifications_Per_Day",
    "Addiction_Level",
    "Caffeine_Intake",
    "Stress_Level_Raw",
    "Behavioral_Risk_Index",
    "Productivity_Flag",
]


_PHYSICAL_ACTIVITY_MAP = {
    "Yes": 5.0,
    "Active": 5.0,
    "High": 5.0,
    "Medium": 3.0,
    "Moderate": 3.0,
    "No": 1.0,
    "Low": 1.0,
    "Inactive": 1.0,
}

_PRODUCTIVITY_IMPACT_MAP = {
    "Yes": 1.0,
    "High": 1.0,
    "Medium": 0.5,
    "Moderate": 0.5,
    "Low": 0.25,
    "No": 0.0,
}


def _coerce_numeric(frame: pd.DataFrame) -> pd.DataFrame:
    for column in NUMERIC_COLUMNS_RAW:
        if column in frame.columns:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
    return frame


def _harmonize_physical_activity(frame: pd.DataFrame) -> pd.DataFrame:
    if "Physical_Activity" in frame.columns:
        values = frame["Physical_Activity"].astype(str).str.strip().str.title()
        numeric = values.map(_PHYSICAL_ACTIVITY_MAP)
        frame["Physical_Activity_Score"] = pd.to_numeric(numeric, errors="coerce")
    if "Physical_Activity_Score" not in frame.columns:
        frame["Physical_Activity_Score"] = np.nan
    return frame


def _harmonize_productivity_impact(frame: pd.DataFrame) -> pd.DataFrame:
    if "Productivity_Impact" in frame.columns:
        values = frame["Productivity_Impact"].astype(str).str.strip().str.title()
        numeric = values.map(_PRODUCTIVITY_IMPACT_MAP)
        frame["Productivity_Impact_Score"] = pd.to_numeric(numeric, errors="coerce")
    if "Productivity_Impact_Score" not in frame.columns:
        frame["Productivity_Impact_Score"] = np.nan
    return frame


def _addiction_category_fill(frame: pd.DataFrame) -> pd.DataFrame:
    addiction_level = frame.get("Addiction_Level")
    if addiction_level is not None:
        derived = pd.cut(
            addiction_level.astype(float),
            bins=[-0.01, 0.33, 0.66, 1.01],
            labels=["Low", "Moderate", "High"],
        ).astype("object")
    else:
        derived = pd.Series([np.nan] * len(frame), index=frame.index)

    if "Addiction_Category" in frame.columns:
        existing = frame["Addiction_Category"].replace({"Unknown": np.nan})
        frame["Addiction_Category"] = existing.fillna(derived).fillna("Moderate")
    else:
        frame["Addiction_Category"] = derived.fillna("Moderate")
    return frame


def _normalize_stress(frame: pd.DataFrame) -> pd.DataFrame:
    if "Stress_Level" not in frame.columns:
        frame["Stress_Level_Norm"] = np.nan
        return frame
    series = frame["Stress_Level"].astype(float)
    max_value = float(series.max()) if len(series) else 1.0
    scale = max_value if max_value > 1.0 else 1.0
    frame["Stress_Level_Norm"] = (series / scale).clip(0.0, 1.0)
    return frame


def _normalize_addiction(frame: pd.DataFrame) -> pd.DataFrame:
    if "Addiction_Level" in frame.columns:
        frame["Addiction_Level_Norm"] = (
            frame["Addiction_Level"].astype(float).clip(0.0, 1.0)
        )
    else:
        frame["Addiction_Level_Norm"] = np.nan
    return frame


def _normalize_region_group(frame: pd.DataFrame) -> pd.DataFrame:
    if "Region_Group" in frame.columns:
        frame["Region_Group"] = frame["Region_Group"].astype(str).str.strip()
        frame.loc[~frame["Region_Group"].isin(["India", "USA"]), "Region_Group"] = "Global"
    return frame


def _impute_basic(frame: pd.DataFrame) -> pd.DataFrame:
    impute_targets = {
        "Social_Media_Hours": frame["Social_Media_Hours"].median()
        if "Social_Media_Hours" in frame.columns
        else 3.0,
        "Gaming_Hours": frame["Gaming_Hours"].median()
        if "Gaming_Hours" in frame.columns
        else 1.5,
        "Notifications_Per_Day": frame["Notifications_Per_Day"].median()
        if "Notifications_Per_Day" in frame.columns
        else 120.0,
        "Physical_Activity_Score": frame["Physical_Activity_Score"].median()
        if "Physical_Activity_Score" in frame.columns
        else 3.0,
        "Caffeine_Intake": frame["Caffeine_Intake"].median()
        if "Caffeine_Intake" in frame.columns
        else 130.0,
        "Productivity_Impact_Score": frame["Productivity_Impact_Score"].median()
        if "Productivity_Impact_Score" in frame.columns
        else 0.5,
        "Anxiety_Level": frame["Anxiety_Level"].median()
        if "Anxiety_Level" in frame.columns
        else 20.0,
        "Depression_Level": frame["Depression_Level"].median()
        if "Depression_Level" in frame.columns
        else 20.0,
    }
    for column, value in impute_targets.items():
        if column in frame.columns:
            fill = value if pd.notna(value) else 0.0
            frame[column] = frame[column].fillna(fill)
    if "Notifications_Per_Day" in frame.columns:
        frame["Notifications_Per_Day"] = frame["Notifications_Per_Day"].clip(lower=0.0)
    if "Screen_Time" in frame.columns:
        frame["Screen_Time"] = frame["Screen_Time"].clip(lower=0.0)
    return frame


def _normalize_for_bri(frame: pd.DataFrame) -> pd.DataFrame:
    screen_time = frame.get("Screen_Time", pd.Series(0.0, index=frame.index))
    sleep_hours = frame.get("Sleep_Hours", pd.Series(7.0, index=frame.index))
    social = frame.get("Social_Media_Hours", pd.Series(2.0, index=frame.index))
    stress = frame.get("Stress_Level_Norm", pd.Series(0.1, index=frame.index))
    frame["Behavioral_Risk_Index_Recomputed"] = (
        BRI_WEIGHTS["Screen_Time"] * (screen_time / 12.0).clip(0.0, 1.0)
        + BRI_WEIGHTS["Stress_Level_Norm"] * stress.clip(0.0, 1.0)
        + BRI_WEIGHTS["Sleep_Hours"] * (sleep_hours / 10.0).clip(0.0, 1.0)
        + BRI_WEIGHTS["Social_Media_Hours"] * (social / 8.0).clip(0.0, 1.0)
    )
    return frame


def clean_dataset(frame: pd.DataFrame) -> pd.DataFrame:
    dataset = frame.copy()
    dataset = _coerce_numeric(dataset)
    dataset = _harmonize_physical_activity(dataset)
    dataset = _harmonize_productivity_impact(dataset)
    dataset = _normalize_region_group(dataset)
    dataset = _normalize_stress(dataset)
    dataset = _normalize_addiction(dataset)
    dataset = _addiction_category_fill(dataset)
    dataset = _impute_basic(dataset)
    dataset = _normalize_for_bri(dataset)
    return dataset


@lru_cache(maxsize=1)
def load_raw_dataset() -> pd.DataFrame:
    return clean_dataset(pd.read_csv(RAW_DATA_PATH))


@lru_cache(maxsize=1)
def load_processed_dataset() -> pd.DataFrame:
    path = PROCESSED_DATA_PATH if PROCESSED_DATA_PATH.exists() else RAW_DATA_PATH
    if path == RAW_DATA_PATH:
        return clean_dataset(pd.read_csv(path))
    return pd.read_csv(path)


def compute_defaults(dataset: pd.DataFrame) -> dict[str, float | str]:
    return {
        "Age": int(round(dataset["Age"].mean())),
        "Gender": dataset["Gender"].mode(dropna=True).iloc[0],
        "User_Type": "Mixed",
        "Region_Group": "Global",
        "Age_Group": dataset["Age_Group"].mode(dropna=True).iloc[0],
        "Screen_Time": round(float(dataset["Screen_Time"].mean()), 1),
        "Social_Media_Hours": round(float(dataset["Social_Media_Hours"].mean()), 1),
        "Gaming_Hours": round(float(dataset["Gaming_Hours"].mean()), 1),
        "Work_Study_Hours": round(float(dataset["Work_Study_Hours"].mean()), 1),
        "Sleep_Hours": round(float(dataset["Sleep_Hours"].mean()), 1),
        "Notifications_Per_Day": round(float(dataset["Notifications_Per_Day"].mean()), 0),
        "Physical_Activity_Score": round(
            float(dataset["Physical_Activity_Score"].mean()), 1
        ),
        "Caffeine_Intake": round(float(dataset["Caffeine_Intake"].mean()), 1),
    }


def compute_options(dataset: pd.DataFrame) -> dict[str, list[str]]:
    return {
        "Gender": sorted(dataset["Gender"].dropna().astype(str).unique().tolist()),
        "User_Type": ["Student", "Professional", "Mixed"],
        "Region_Group": ["India", "USA", "Global"],
        "Age_Group": sorted(dataset["Age_Group"].dropna().astype(str).unique().tolist()),
    }


def dataset_ranges(
    dataset: pd.DataFrame, columns: list[str]
) -> dict[str, dict[str, float]]:
    return {
        column: {
            "min": float(dataset[column].min()),
            "max": float(dataset[column].max()),
            "mean": float(dataset[column].mean()),
            "p25": float(dataset[column].quantile(0.25)),
            "p75": float(dataset[column].quantile(0.75)),
        }
        for column in columns
        if column in dataset.columns
    }


def percentile_rank(series: pd.Series, value: float) -> float:
    if len(series) == 0:
        return 50.0
    return float((series <= value).mean() * 100.0)


def behavioral_risk_index(
    screen_time: float,
    stress_norm: float,
    sleep_hours: float,
    social_media_hours: float,
) -> float:
    return (
        BRI_WEIGHTS["Screen_Time"] * min(max(screen_time / 12.0, 0.0), 1.0)
        + BRI_WEIGHTS["Stress_Level_Norm"] * min(max(stress_norm, 0.0), 1.0)
        + BRI_WEIGHTS["Sleep_Hours"] * min(max(sleep_hours / 10.0, 0.0), 1.0)
        + BRI_WEIGHTS["Social_Media_Hours"] * min(max(social_media_hours / 8.0, 0.0), 1.0)
    )


def ensure_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
