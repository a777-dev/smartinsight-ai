from __future__ import annotations

import json
from functools import lru_cache

import joblib
import numpy as np
import pandas as pd

from src.config import (
    ADDICTION_LEVELS,
    ADDICTION_MODEL_PATH,
    CLUSTER_BUNDLE_PATH,
    CLUSTER_FEATURES,
    DEFAULT_INPUTS,
    METADATA_PATH,
    MODEL_FEATURES,
    PERCENTILE_FIELDS,
    PREPROCESSOR_PATH,
    PRODUCTIVITY_MODEL_PATH,
    STRESS_MODEL_PATH,
)
from src.data import (
    behavioral_risk_index,
    load_processed_dataset,
    percentile_rank,
)
from src.training import ensure_artifacts


@lru_cache(maxsize=1)
def load_artifacts() -> dict[str, object]:
    ensure_artifacts()
    return {
        "preprocessor": joblib.load(PREPROCESSOR_PATH),
        "stress_model": joblib.load(STRESS_MODEL_PATH),
        "addiction_model": joblib.load(ADDICTION_MODEL_PATH),
        "productivity_model": joblib.load(PRODUCTIVITY_MODEL_PATH),
        "cluster_bundle": joblib.load(CLUSTER_BUNDLE_PATH),
        "metadata": json.loads(METADATA_PATH.read_text(encoding="utf-8")),
    }


def load_reference_dataset() -> pd.DataFrame:
    return load_processed_dataset().copy()


def normalize_optional(value):
    if value in (None, "", "Use dataset average"):
        return None
    return value


def build_profile(user_inputs: dict[str, object], defaults: dict[str, object]) -> dict[str, object]:
    profile: dict[str, object] = {}
    for feature in MODEL_FEATURES:
        raw_value = normalize_optional(user_inputs.get(feature))
        if raw_value is None:
            profile[feature] = defaults.get(feature, DEFAULT_INPUTS.get(feature))
        else:
            profile[feature] = raw_value

    for numeric_feature in [
        "Age",
        "Screen_Time",
        "Social_Media_Hours",
        "Gaming_Hours",
        "Work_Study_Hours",
        "Sleep_Hours",
        "Notifications_Per_Day",
        "Physical_Activity_Score",
        "Caffeine_Intake",
    ]:
        profile[numeric_feature] = float(profile[numeric_feature])
    return profile


def profile_to_frame(profile: dict[str, object]) -> pd.DataFrame:
    return pd.DataFrame([profile])[MODEL_FEATURES]


def _predict_stress_score(frame: pd.DataFrame) -> float:
    artifacts = load_artifacts()
    transformed = artifacts["preprocessor"].transform(frame[MODEL_FEATURES])
    return float(np.clip(artifacts["stress_model"].predict(transformed)[0], 0.0, 1.0))


def _predict_addiction(frame: pd.DataFrame) -> dict[str, object]:
    artifacts = load_artifacts()
    transformed = artifacts["preprocessor"].transform(frame[MODEL_FEATURES])
    proba = artifacts["addiction_model"].predict_proba(transformed)[0]
    classes = artifacts["addiction_model"].classes_.tolist()
    probabilities = {cls: float(proba[index]) for index, cls in enumerate(classes)}
    severity = (
        probabilities.get("Low", 0.0) * 0.0
        + probabilities.get("Moderate", 0.0) * 0.5
        + probabilities.get("High", 0.0) * 1.0
    )
    predicted = max(probabilities, key=probabilities.get)
    return {
        "label": predicted,
        "severity": float(np.clip(severity, 0.0, 1.0)),
        "probabilities": probabilities,
    }


def _predict_productivity(frame: pd.DataFrame) -> dict[str, object]:
    artifacts = load_artifacts()
    transformed = artifacts["preprocessor"].transform(frame[MODEL_FEATURES])
    model = artifacts["productivity_model"]
    proba = model.predict_proba(transformed)[0]
    impact_index = list(model.classes_).index(1) if 1 in model.classes_ else 0
    impact_probability = float(proba[impact_index])
    productivity_score = float(np.clip(1.0 - impact_probability, 0.0, 1.0))
    return {
        "impact_probability": impact_probability,
        "productivity_score": productivity_score,
    }


def _percentiles(profile: dict[str, object], dataset: pd.DataFrame) -> dict[str, float]:
    return {
        field: round(percentile_rank(dataset[field], float(profile[field])), 1)
        for field in PERCENTILE_FIELDS
        if field in dataset.columns
    }


def _assign_cluster(profile: dict[str, object], stress_norm: float) -> dict[str, str]:
    artifacts = load_artifacts()
    bundle = artifacts["cluster_bundle"]
    cluster_input = {
        "Screen_Time": float(profile["Screen_Time"]),
        "Social_Media_Hours": float(profile["Social_Media_Hours"]),
        "Sleep_Hours": float(profile["Sleep_Hours"]),
        "Notifications_Per_Day": float(profile["Notifications_Per_Day"]),
        "Physical_Activity_Score": float(profile["Physical_Activity_Score"]),
        "Behavioral_Risk_Index": behavioral_risk_index(
            float(profile["Screen_Time"]),
            stress_norm,
            float(profile["Sleep_Hours"]),
            float(profile["Social_Media_Hours"]),
        ),
        "Stress_Level_Norm": float(stress_norm),
    }
    frame = pd.DataFrame([cluster_input])[CLUSTER_FEATURES]
    scaled = bundle["scaler"].transform(frame)
    cluster_id = int(bundle["model"].predict(scaled)[0])
    label = bundle["label_map"].get(cluster_id) or bundle["label_map"].get(str(cluster_id), "Balanced Users")
    description = bundle["description_map"].get(cluster_id) or bundle["description_map"].get(str(cluster_id), "")
    return {"id": cluster_id, "label": label, "description": description}


def _radar_payload(
    profile: dict[str, object],
    stress_norm: float,
    productivity_score: float,
    dataset: pd.DataFrame,
) -> dict[str, list[float]]:
    user_values = {
        "Sleep": min(float(profile["Sleep_Hours"]) / 9.0, 1.0),
        "Screen Time": 1.0 - min(float(profile["Screen_Time"]) / 12.0, 1.0),
        "Social Media": 1.0 - min(float(profile["Social_Media_Hours"]) / 6.0, 1.0),
        "Stress": 1.0 - float(stress_norm),
        "Activity": min(float(profile["Physical_Activity_Score"]) / 5.0, 1.0),
    }
    averages = {
        "Sleep": min(dataset["Sleep_Hours"].mean() / 9.0, 1.0),
        "Screen Time": 1.0 - min(dataset["Screen_Time"].mean() / 12.0, 1.0),
        "Social Media": 1.0 - min(dataset["Social_Media_Hours"].mean() / 6.0, 1.0),
        "Stress": 1.0 - float(dataset["Stress_Level_Norm"].mean()),
        "Activity": min(dataset["Physical_Activity_Score"].mean() / 5.0, 1.0),
    }
    axes = list(user_values.keys())
    return {
        "axes": axes,
        "user": [round(float(user_values[a]) * 100, 1) for a in axes],
        "average": [round(float(averages[a]) * 100, 1) for a in axes],
    }


def _lifestyle_score(
    profile: dict[str, object], stress_norm: float, productivity_score: float
) -> dict[str, object]:
    sleep_score = min(float(profile["Sleep_Hours"]) / 8.0, 1.0)
    screen_score = max(0.0, 1.0 - float(profile["Screen_Time"]) / 12.0)
    stress_score = 1.0 - float(stress_norm)
    components = {
        "Sleep": round(sleep_score * 100, 1),
        "Screen Time": round(screen_score * 100, 1),
        "Stress": round(stress_score * 100, 1),
        "Productivity": round(productivity_score * 100, 1),
    }
    weights = {"Sleep": 0.30, "Screen Time": 0.25, "Stress": 0.25, "Productivity": 0.20}
    total = sum(components[k] * weights[k] for k in weights)
    return {"total": round(total, 1), "components": components}


def _build_headline(stress_norm: float, productivity_score: float, addiction_label: str) -> str:
    stress_descriptor = (
        "elevated"
        if stress_norm >= 0.55
        else "moderate"
        if stress_norm >= 0.3
        else "calm"
    )
    productivity_descriptor = (
        "strong"
        if productivity_score >= 0.7
        else "uneven"
        if productivity_score >= 0.5
        else "fragile"
    )
    return (
        f"Your behavioral read is {stress_descriptor} stress with {productivity_descriptor} "
        f"productivity and {addiction_label.lower()} addiction risk."
    )


def analyze_profile(
    user_inputs: dict[str, object], reference_df: pd.DataFrame | None = None
) -> dict[str, object]:
    artifacts = load_artifacts()
    metadata = artifacts["metadata"]
    dataset = reference_df if reference_df is not None else load_reference_dataset()

    profile = build_profile(user_inputs, metadata["defaults"])
    frame = profile_to_frame(profile)

    stress_norm = _predict_stress_score(frame)
    addiction = _predict_addiction(frame)
    productivity = _predict_productivity(frame)
    bri = behavioral_risk_index(
        float(profile["Screen_Time"]),
        stress_norm,
        float(profile["Sleep_Hours"]),
        float(profile["Social_Media_Hours"]),
    )

    cluster = _assign_cluster(profile, stress_norm)
    percentiles = _percentiles(profile, dataset)
    radar = _radar_payload(profile, stress_norm, productivity["productivity_score"], dataset)
    lifestyle = _lifestyle_score(profile, stress_norm, productivity["productivity_score"])
    headline = _build_headline(
        stress_norm, productivity["productivity_score"], addiction["label"]
    )

    warnings: list[str] = []
    if float(profile["Sleep_Hours"]) < 5.0 and float(profile["Screen_Time"]) > 8.0:
        warnings.append(
            "Critical pattern: low sleep combined with very high screen time."
        )

    return {
        "profile": profile,
        "stress_level": round(stress_norm, 3),
        "stress_pct": round(stress_norm * 100.0, 1),
        "addiction": addiction,
        "productivity": productivity,
        "behavioral_risk_index": round(float(bri), 3),
        "cluster": cluster,
        "percentiles": percentiles,
        "radar": radar,
        "lifestyle_score": lifestyle,
        "headline": headline,
        "warnings": warnings,
        "feature_importance": metadata["feature_importance"],
    }


def local_feature_impacts(profile: dict[str, object]) -> dict[str, dict[str, float]]:
    """For each simulation feature, perturb by +/- and capture model deltas."""
    artifacts = load_artifacts()
    metadata = artifacts["metadata"]
    base_frame = profile_to_frame(profile)
    base_stress = _predict_stress_score(base_frame)
    base_productivity = _predict_productivity(base_frame)["productivity_score"]
    base_addiction = _predict_addiction(base_frame)["severity"]

    deltas = {
        "Screen_Time": 1.0,
        "Social_Media_Hours": 0.5,
        "Sleep_Hours": 0.5,
        "Notifications_Per_Day": 25.0,
        "Physical_Activity_Score": 0.5,
        "Caffeine_Intake": 25.0,
    }

    impacts: dict[str, dict[str, float]] = {}
    for feature, delta in deltas.items():
        if feature not in profile:
            continue
        upper_profile = dict(profile)
        upper_profile[feature] = float(profile[feature]) + delta
        upper_frame = profile_to_frame(upper_profile)
        stress_up = _predict_stress_score(upper_frame)
        prod_up = _predict_productivity(upper_frame)["productivity_score"]
        addiction_up = _predict_addiction(upper_frame)["severity"]
        impacts[feature] = {
            "stress": round(float(stress_up - base_stress), 4),
            "productivity": round(float(prod_up - base_productivity), 4),
            "addiction": round(float(addiction_up - base_addiction), 4),
        }
    return impacts
