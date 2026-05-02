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

# CTR tier labels (output classes)
CTR_TIERS = ["low", "medium", "high"]


# ── preprocessing ──────────────────────────────────────────────────────────────
def preprocess_for_inference(df: pd.DataFrame, encoders: dict) -> pd.DataFrame:
    """
    Prepare a raw dataframe for inference (no target column needed).
    Uses already-fitted encoders loaded from disk.

    Args:
        df:       Raw input dataframe with campaign/ad/audience columns
        encoders: Dict of {col_name: fitted LabelEncoder} from training

    Returns:
        Encoded dataframe with exactly FEATURE_COLS columns, in order.
    """
    df = df.copy()

    # Drop metadata columns if present
    cols_to_drop = [c for c in DROP_COLS if c in df.columns]
    df = df.drop(columns=cols_to_drop)

    # Impute missing values
    for col in IMPUTE_MEDIAN_COLS:
        if col in df.columns:
            df[col] = df[col].fillna(df[col].median())

    # Encode using the saved encoders from training
    for col, le in encoders.items():
        if col in df.columns:
            # Handle unseen labels gracefully
            known = set(le.classes_)
            df[col] = df[col].astype(str).apply(
                lambda x: x if x in known else le.classes_[0]
            )
            df[col] = le.transform(df[col])

    # Keep only the exact feature columns the model was trained on
    df = df[[c for c in FEATURE_COLS if c in df.columns]]

    return df


# ── artifact loading ───────────────────────────────────────────────────────────
def load_model():
    """Load the trained model from models/model.pkl"""
    path = os.path.join(MODELS_DIR, "model.pkl")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Model not found at {path}. Run train.py first.")
    return joblib.load(path)


def load_encoders():
    """Load the fitted encoders from models/encoders.pkl"""
    path = os.path.join(MODELS_DIR, "encoders.pkl")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Encoders not found at {path}. Run train.py first.")
    return joblib.load(path)


def load_feature_cols():
    """Load the feature column list from models/feature_cols.pkl"""
    path = os.path.join(MODELS_DIR, "feature_cols.pkl")
    if not os.path.exists(path):
        raise FileNotFoundError(f"feature_cols not found at {path}. Run train.py first.")
    return joblib.load(path)
