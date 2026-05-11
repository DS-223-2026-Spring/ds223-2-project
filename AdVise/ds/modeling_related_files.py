"""
modeling_related_files.py
AdVise — Milestone 3
Shared feature definitions, preprocessing helpers, and artifact loading utilities.
Import from this module in train.py, predict.py, and any other DS scripts.
"""

import os
import joblib
import pandas as pd
from sklearn.preprocessing import LabelEncoder

# ── paths ──────────────────────────────────────────────────────────────────────
THIS_DIR   = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(THIS_DIR, "models")

# ── feature definitions ────────────────────────────────────────────────────────
TARGET = "ctr"

# All supported prediction targets
ALL_TARGETS = {
    "ctr":             "ctr_tier",
    "conversion_rate": "conversion_rate_tier",
    "reach_score":     "reach_score_tier",
}

# Targets we train and predict for (single source of truth)
TRAIN_TARGETS = ["ctr", "conversion_rate", "reach_score"]

# Which target to use based on campaign_intent
INTENT_TO_TARGET = {
    "awareness": "reach_score",
    "sales":     "conversion_rate",
    "leads":     "conversion_rate",
    "traffic":   "ctr",
    "engagement":"ctr",
}

# Columns dropped before training — not predictive or constant
DROP_COLS = ["budget", "is_synthetic", "data_source"]

# Columns imputed with median when missing
IMPUTE_MEDIAN_COLS = ["engagement_score"]

# Final 21 features used by the trained model (in order)
FEATURE_COLS = [
    "platform", "duration_days", "campaign_intent", "product_type",
    "cta_type", "age", "gender", "location", "interests",
    "audience_temperature", "customer_type", "career", "creative_type",
    "copy_text_length", "aspect_ratio", "visual_complexity", "has_person",
    "conversion_rate", "engagement_score", "reach_score", "lead_rate",
]

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add derived features — must match what train.py produces."""
    df = df.copy()

    if "engagement_score" in df.columns and "duration_days" in df.columns:
        df["engagement_per_day"] = df["engagement_score"] / (df["duration_days"] + 1)

    if "budget" in df.columns and "duration_days" in df.columns:
        df["budget_per_day"] = df["budget"] / (df["duration_days"] + 1)

    if "copy_text_length" in df.columns:
        df["copy_length_bucket"] = pd.cut(
            df["copy_text_length"],
            bins=[0, 10, 30, 9999],
            labels=["short", "medium", "long"]
        ).astype(str)

    # Multi-metric mean — exclude the target being predicted to avoid leakage
    # Only use lead_rate as it's never a direct target
    if "lead_rate" in df.columns:
        df["multi_metric_mean"] = df["lead_rate"]

    return df

# CTR tier labels (output classes)
CTR_TIERS = ["low", "medium", "high"]


# ── preprocessing ──────────────────────────────────────────────────────────────
def preprocess_for_inference(df: pd.DataFrame, encoders: dict, target: str = "ctr") -> pd.DataFrame:
    """
    Prepare a raw dataframe for inference (no target column needed).
    Uses already-fitted encoders loaded from disk.
    """
    df = df.copy()

    # Drop metadata columns if present
    cols_to_drop = [c for c in DROP_COLS if c in df.columns]
    df = df.drop(columns=cols_to_drop)

    # Drop ALL target-like columns so they don't leak into features
    all_targets = ["ctr", "conversion_rate", "reach_score",
                   "engagement_score", "lead_rate", "_target"]
    cols_to_remove = [c for c in all_targets if c in df.columns]
    df = df.drop(columns=cols_to_remove)

    # Impute missing values
    for col in IMPUTE_MEDIAN_COLS:
        if col in df.columns:
            df[col] = df[col].fillna(df[col].median())

    # Encode using the saved encoders from training
    for col, le in encoders.items():
        if col in df.columns:
            known = set(le.classes_)
            df[col] = df[col].astype(str).apply(
                lambda x: x if x in known else le.classes_[0]
            )
            df[col] = le.transform(df[col])

    # Keep only the columns the model was trained on, in exact order
    feature_cols = load_feature_cols(target)
    available = [c for c in feature_cols if c in df.columns]
    df = df[available]

    return df


# ── artifact loading ───────────────────────────────────────────────────────────
def load_model(target: str = "ctr"):
    """Load the trained model for a given target."""
    path = os.path.join(MODELS_DIR, f"model_{target}.pkl")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Model not found at {path}. Run train.py first.")
    return joblib.load(path)


def load_encoders(target: str = "ctr"):
    """Load the fitted encoders for a given target."""
    path = os.path.join(MODELS_DIR, f"encoders_{target}.pkl")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Encoders not found at {path}. Run train.py first.")
    return joblib.load(path)


def load_feature_cols(target: str = "ctr"):
    """Load the feature column list for a given target."""
    path = os.path.join(MODELS_DIR, f"feature_cols_{target}.pkl")
    if not os.path.exists(path):
        raise FileNotFoundError(f"feature_cols not found at {path}. Run train.py first.")
    return joblib.load(path)

def get_feature_importance(target: str = "ctr") -> pd.DataFrame:
    """Return a sorted dataframe of feature importances for a trained model."""
    model = load_model(target)
    feature_cols = load_feature_cols(target)
    importances = model.feature_importances_
    df = pd.DataFrame({
        "feature": feature_cols,
        "importance": importances
    }).sort_values("importance", ascending=False).reset_index(drop=True)
    return df