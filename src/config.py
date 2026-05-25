from __future__ import annotations

from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
RAW_DATA_PATH = ROOT_DIR / "unified_behavioral_intelligence.csv"
PROCESSED_DATA_PATH = ROOT_DIR / "data" / "processed_behavioral_data.csv"
MODELS_DIR = ROOT_DIR / "models"

STRESS_MODEL_PATH = MODELS_DIR / "stress_model.pkl"
ADDICTION_MODEL_PATH = MODELS_DIR / "addiction_model.pkl"
PRODUCTIVITY_MODEL_PATH = MODELS_DIR / "productivity_model.pkl"
PREPROCESSOR_PATH = MODELS_DIR / "preprocessor.pkl"
CLUSTER_BUNDLE_PATH = MODELS_DIR / "cluster_bundle.pkl"
METADATA_PATH = MODELS_DIR / "model_metadata.json"

RANDOM_STATE = 42
SCATTER_SAMPLE_SIZE = 4000

# Region groupings supported by the dataset
REGION_GROUPS = ["India", "USA", "Global"]
USER_TYPES = ["Student", "Professional", "Mixed"]
ADDICTION_LEVELS = ["Low", "Moderate", "High"]

# Numeric features used directly by ML pipelines.
NUMERIC_FEATURES = [
    "Age",
    "Screen_Time",
    "Social_Media_Hours",
    "Gaming_Hours",
    "Work_Study_Hours",
    "Sleep_Hours",
    "Notifications_Per_Day",
    "Physical_Activity_Score",
    "Caffeine_Intake",
]

CATEGORICAL_FEATURES = ["Gender", "User_Type", "Region_Group", "Age_Group"]

MODEL_FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES

# Lifestyle slider inputs used in the interactive simulator + risk prediction UI.
SIMULATION_FEATURES = [
    "Screen_Time",
    "Social_Media_Hours",
    "Sleep_Hours",
    "Notifications_Per_Day",
    "Physical_Activity_Score",
    "Caffeine_Intake",
    "Work_Study_Hours",
    "Gaming_Hours",
]

CLUSTER_FEATURES = [
    "Screen_Time",
    "Social_Media_Hours",
    "Sleep_Hours",
    "Notifications_Per_Day",
    "Physical_Activity_Score",
    "Behavioral_Risk_Index",
    "Stress_Level_Norm",
]

CLUSTER_LABELS = {
    "burnout": "Burnout Users",
    "balanced": "Balanced Users",
    "hyper": "Hyper-Connected Users",
    "achiever": "Sleep-Deprived Achievers",
    "low_risk": "Low-Risk Users",
}

CLUSTER_DESCRIPTIONS = {
    "Burnout Users": "Long screen days, sleep deficit, elevated stress, and impaired productivity.",
    "Balanced Users": "Healthy sleep, moderate digital usage, and stable productivity signals.",
    "Hyper-Connected Users": "High notifications and social media intensity with reduced offline activity.",
    "Sleep-Deprived Achievers": "High work intensity and productivity but chronic sleep deficit.",
    "Low-Risk Users": "Light digital intensity with healthy lifestyle indicators across the board.",
}

CLUSTER_ICONS = {
    "Burnout Users": "BU",
    "Balanced Users": "BA",
    "Hyper-Connected Users": "HC",
    "Sleep-Deprived Achievers": "SD",
    "Low-Risk Users": "LR",
}

# Mapping for displaying field names in the UI.
UI_FIELD_LABELS = {
    "Age": "Age",
    "Gender": "Gender",
    "User_Type": "User Type",
    "Region_Group": "Region",
    "Age_Group": "Age Group",
    "Screen_Time": "Screen Time (h/day)",
    "Social_Media_Hours": "Social Media (h/day)",
    "Gaming_Hours": "Gaming (h/day)",
    "Work_Study_Hours": "Work/Study (h/day)",
    "Sleep_Hours": "Sleep (h/day)",
    "Notifications_Per_Day": "Notifications/day",
    "Physical_Activity_Score": "Physical Activity (1-5)",
    "Caffeine_Intake": "Caffeine Intake",
    "Stress_Level_Norm": "Stress (0-1)",
    "Behavioral_Risk_Index": "Behavioral Risk Index",
    "Addiction_Level_Norm": "Addiction Level (0-1)",
    "Productivity_Score": "Productivity Score",
}

PERCENTILE_FIELDS = [
    "Screen_Time",
    "Social_Media_Hours",
    "Sleep_Hours",
    "Notifications_Per_Day",
    "Physical_Activity_Score",
]

CORRELATION_FIELDS = [
    "Screen_Time",
    "Social_Media_Hours",
    "Sleep_Hours",
    "Gaming_Hours",
    "Work_Study_Hours",
    "Notifications_Per_Day",
    "Physical_Activity_Score",
    "Caffeine_Intake",
    "Stress_Level_Norm",
    "Addiction_Level_Norm",
    "Behavioral_Risk_Index",
]

# Behavioral Risk Index weights from developer spec.
BRI_WEIGHTS = {
    "Screen_Time": 0.35,
    "Stress_Level_Norm": 0.30,
    "Sleep_Hours": -0.20,
    "Social_Media_Hours": 0.15,
}

# Lifestyle score weights for the consolidated wellness number (0-100).
LIFESTYLE_SCORE_WEIGHTS = {
    "Sleep": 0.30,
    "Screen Time": 0.25,
    "Stress": 0.25,
    "Productivity": 0.20,
}

RADAR_AXES = ["Sleep", "Screen Time", "Social Media", "Stress", "Activity"]

# Defaults applied when an optional input is omitted.
DEFAULT_INPUTS = {
    "Age": 28,
    "Gender": "Male",
    "User_Type": "Mixed",
    "Region_Group": "Global",
    "Age_Group": "Young Adult",
    "Screen_Time": 6.4,
    "Social_Media_Hours": 3.0,
    "Gaming_Hours": 1.8,
    "Work_Study_Hours": 3.1,
    "Sleep_Hours": 6.9,
    "Notifications_Per_Day": 120.0,
    "Physical_Activity_Score": 3.0,
    "Caffeine_Intake": 130.0,
}

# Palette aligned with the master UI/UX brief.
PALETTE = {
    "background":  "#0D1424",
    "foreground":  "#F0F4FF",
    "primary":     "#6366F1",
    "secondary":   "#10B981",
    "accent":      "#F59E0B",
    "muted":       "rgba(255,255,255,0.06)",
    "border":      "rgba(255,255,255,0.10)",
    "danger":      "#EF4444",
    "soft_text":   "#94A3B8",
}

REGION_PALETTE = {
    "India": "#F59E0B",
    "USA":   "#818CF8",
    "Global": "#10B981",
}

USER_PALETTE = {
    "Student":      "#818CF8",
    "Professional": "#F59E0B",
    "Mixed":        "#10B981",
}

ADDICTION_PALETTE = {
    "Low": "#10B981",
    "Moderate": "#F59E0B",
    "High": "#EF4444",
}
