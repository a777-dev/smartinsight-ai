from __future__ import annotations

import json

import joblib
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, f1_score, mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.config import (
    ADDICTION_LEVELS,
    ADDICTION_MODEL_PATH,
    CATEGORICAL_FEATURES,
    CLUSTER_BUNDLE_PATH,
    CLUSTER_FEATURES,
    CORRELATION_FIELDS,
    METADATA_PATH,
    MODEL_FEATURES,
    MODELS_DIR,
    NUMERIC_FEATURES,
    PREPROCESSOR_PATH,
    PROCESSED_DATA_PATH,
    PRODUCTIVITY_MODEL_PATH,
    RANDOM_STATE,
    RAW_DATA_PATH,
    STRESS_MODEL_PATH,
    UI_FIELD_LABELS,
)
from src.data import (
    clean_dataset,
    compute_defaults,
    compute_options,
    dataset_ranges,
    ensure_directory,
)


def build_preprocessor() -> ColumnTransformer:
    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            (
                "encoder",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
            ),
        ]
    )
    return ColumnTransformer(
        transformers=[
            ("num", numeric_pipeline, NUMERIC_FEATURES),
            ("cat", categorical_pipeline, CATEGORICAL_FEATURES),
        ],
        remainder="drop",
        sparse_threshold=0.0,
    )


def aggregate_feature_importances(
    importances: np.ndarray, feature_names: list[str]
) -> dict[str, float]:
    aggregated: dict[str, float] = {}
    for feature_name, importance in zip(feature_names, importances, strict=True):
        base_name = feature_name.split("__", 1)[-1]
        matched_name = base_name
        for candidate in MODEL_FEATURES:
            if base_name == candidate or base_name.startswith(f"{candidate}_"):
                matched_name = candidate
                break
        aggregated[matched_name] = aggregated.get(matched_name, 0.0) + float(importance)
    total = sum(aggregated.values()) or 1.0
    return {
        feature: round(value / total, 6)
        for feature, value in sorted(
            aggregated.items(), key=lambda item: item[1], reverse=True
        )
    }


def _stress_target(dataset: pd.DataFrame) -> pd.Series:
    return dataset["Stress_Level_Norm"].astype(float).clip(0.0, 1.0)


def _addiction_target(dataset: pd.DataFrame) -> pd.Series:
    target = dataset["Addiction_Category"].astype(str)
    target = target.where(target.isin(ADDICTION_LEVELS), other="Moderate")
    return target


def _productivity_target(dataset: pd.DataFrame) -> pd.Series:
    return dataset["Productivity_Flag"].astype(int)


def describe_cluster(label: str, center: pd.Series) -> str:
    sleep = center.get("Sleep_Hours", 7.0)
    screen = center.get("Screen_Time", 6.0)
    stress = center.get("Stress_Level_Norm", 0.2)
    return (
        f"Screen {screen:.1f}h | Sleep {sleep:.1f}h | Stress {stress:.2f} | "
        f"BRI {center.get('Behavioral_Risk_Index', 1.2):.2f}"
    )


def build_cluster_bundle(dataset: pd.DataFrame) -> tuple[dict[str, object], pd.DataFrame]:
    cluster_frame = dataset[CLUSTER_FEATURES].copy()
    cluster_frame["Behavioral_Risk_Index"] = dataset["Behavioral_Risk_Index_Recomputed"]
    scaler = StandardScaler()
    scaled_values = scaler.fit_transform(cluster_frame.fillna(cluster_frame.median()))
    kmeans = KMeans(n_clusters=5, n_init=20, random_state=RANDOM_STATE)
    cluster_ids = kmeans.fit_predict(scaled_values)

    centers = pd.DataFrame(
        scaler.inverse_transform(kmeans.cluster_centers_), columns=CLUSTER_FEATURES
    )

    burnout_id = int(centers["Behavioral_Risk_Index"].idxmax())

    remaining = [cid for cid in centers.index.tolist() if cid != burnout_id]

    notif_series = centers.loc[remaining, "Notifications_Per_Day"]
    hyper_id = int(notif_series.idxmax())

    remaining = [cid for cid in remaining if cid != hyper_id]
    sleep_series = centers.loc[remaining, "Sleep_Hours"]
    achiever_id = int(sleep_series.idxmin())

    remaining = [cid for cid in remaining if cid != achiever_id]
    bri_series = centers.loc[remaining, "Behavioral_Risk_Index"]
    low_risk_id = int(bri_series.idxmin())

    remaining = [cid for cid in remaining if cid != low_risk_id]
    balanced_id = int(remaining[0])

    label_map = {
        burnout_id: "Burnout Users",
        hyper_id: "Hyper-Connected Users",
        achiever_id: "Sleep-Deprived Achievers",
        low_risk_id: "Low-Risk Users",
        balanced_id: "Balanced Users",
    }
    description_map = {
        cluster_id: describe_cluster(label_map[cluster_id], centers.loc[cluster_id])
        for cluster_id in centers.index.tolist()
    }

    labeled = dataset.copy()
    labeled["Cluster_Id"] = cluster_ids
    labeled["Cluster_Label"] = labeled["Cluster_Id"].map(label_map)
    labeled["Cluster_Description"] = labeled["Cluster_Id"].map(description_map)

    bundle = {
        "model": kmeans,
        "scaler": scaler,
        "features": CLUSTER_FEATURES,
        "label_map": label_map,
        "description_map": description_map,
        "centers": centers.to_dict(orient="index"),
    }
    return bundle, labeled


def artifacts_exist() -> bool:
    required = [
        STRESS_MODEL_PATH,
        ADDICTION_MODEL_PATH,
        PRODUCTIVITY_MODEL_PATH,
        PREPROCESSOR_PATH,
        CLUSTER_BUNDLE_PATH,
        METADATA_PATH,
        PROCESSED_DATA_PATH,
    ]
    return all(path.exists() for path in required)


def ensure_artifacts(force: bool = False) -> dict[str, object]:
    if force or not artifacts_exist():
        return train_models()
    return json.loads(METADATA_PATH.read_text(encoding="utf-8"))


def train_models() -> dict[str, object]:
    ensure_directory(MODELS_DIR)
    ensure_directory(PROCESSED_DATA_PATH.parent)

    raw_dataset = clean_dataset(pd.read_csv(RAW_DATA_PATH))

    defaults = compute_defaults(raw_dataset)
    options = compute_options(raw_dataset)
    ranges = dataset_ranges(raw_dataset, NUMERIC_FEATURES + CORRELATION_FIELDS)

    features = raw_dataset[MODEL_FEATURES].copy()
    stress_target = _stress_target(raw_dataset)
    addiction_target = _addiction_target(raw_dataset)
    productivity_target = _productivity_target(raw_dataset)

    (
        x_train,
        x_test,
        stress_train,
        stress_test,
        addiction_train,
        addiction_test,
        productivity_train,
        productivity_test,
    ) = train_test_split(
        features,
        stress_target,
        addiction_target,
        productivity_target,
        test_size=0.2,
        random_state=RANDOM_STATE,
        stratify=addiction_target,
    )

    preprocessor = build_preprocessor()
    x_train_transformed = preprocessor.fit_transform(x_train[MODEL_FEATURES])
    x_test_transformed = preprocessor.transform(x_test[MODEL_FEATURES])

    stress_model = RandomForestRegressor(
        n_estimators=250,
        max_depth=14,
        min_samples_leaf=3,
        random_state=RANDOM_STATE,
        n_jobs=1,
    )
    stress_model.fit(x_train_transformed, stress_train)

    addiction_model = RandomForestClassifier(
        n_estimators=300,
        max_depth=14,
        min_samples_leaf=2,
        random_state=RANDOM_STATE,
        class_weight="balanced_subsample",
        n_jobs=1,
    )
    addiction_model.fit(x_train_transformed, addiction_train)

    productivity_model = RandomForestClassifier(
        n_estimators=250,
        max_depth=12,
        min_samples_leaf=3,
        random_state=RANDOM_STATE,
        class_weight="balanced_subsample",
        n_jobs=1,
    )
    productivity_model.fit(x_train_transformed, productivity_train)

    stress_predictions = stress_model.predict(x_test_transformed)
    addiction_predictions = addiction_model.predict(x_test_transformed)
    productivity_predictions = productivity_model.predict(x_test_transformed)

    stress_rmse = float(
        np.sqrt(mean_squared_error(stress_test, stress_predictions))
    )
    addiction_accuracy = float(accuracy_score(addiction_test, addiction_predictions))
    addiction_f1 = float(
        f1_score(addiction_test, addiction_predictions, average="weighted")
    )
    productivity_accuracy = float(
        accuracy_score(productivity_test, productivity_predictions)
    )
    productivity_f1 = float(
        f1_score(productivity_test, productivity_predictions, average="weighted")
    )

    feature_names = preprocessor.get_feature_names_out().tolist()
    feature_importance = {
        "stress": aggregate_feature_importances(
            stress_model.feature_importances_, feature_names
        ),
        "addiction": aggregate_feature_importances(
            addiction_model.feature_importances_, feature_names
        ),
        "productivity": aggregate_feature_importances(
            productivity_model.feature_importances_, feature_names
        ),
    }

    cluster_bundle, processed_dataset = build_cluster_bundle(raw_dataset)
    processed_dataset.to_csv(PROCESSED_DATA_PATH, index=False)

    dump_kwargs = {"compress": 3}
    joblib.dump(stress_model, STRESS_MODEL_PATH, **dump_kwargs)
    joblib.dump(addiction_model, ADDICTION_MODEL_PATH, **dump_kwargs)
    joblib.dump(productivity_model, PRODUCTIVITY_MODEL_PATH, **dump_kwargs)
    joblib.dump(preprocessor, PREPROCESSOR_PATH, **dump_kwargs)
    joblib.dump(cluster_bundle, CLUSTER_BUNDLE_PATH, **dump_kwargs)

    metadata = {
        "feature_order": MODEL_FEATURES,
        "numeric_features": NUMERIC_FEATURES,
        "categorical_features": CATEGORICAL_FEATURES,
        "field_labels": UI_FIELD_LABELS,
        "defaults": defaults,
        "options": options,
        "ranges": ranges,
        "metrics": {
            "stress_rmse": round(stress_rmse, 4),
            "addiction_accuracy": round(addiction_accuracy, 4),
            "addiction_f1": round(addiction_f1, 4),
            "productivity_accuracy": round(productivity_accuracy, 4),
            "productivity_f1": round(productivity_f1, 4),
        },
        "feature_importance": feature_importance,
        "addiction_classes": addiction_model.classes_.tolist(),
        "dataset_summary": {
            "rows": int(len(raw_dataset)),
            "correlation_fields": CORRELATION_FIELDS,
            "region_distribution": raw_dataset["Region_Group"].value_counts().to_dict(),
            "user_distribution": raw_dataset["User_Type"].value_counts().to_dict(),
        },
        "cluster_centers": cluster_bundle["centers"],
        "cluster_labels": cluster_bundle["label_map"],
        "cluster_descriptions": cluster_bundle["description_map"],
    }
    METADATA_PATH.write_text(json.dumps(metadata, indent=2, default=str), encoding="utf-8")
    return metadata
