"""
train.py
AdVise — Milestone 4
Final model training script with feature engineering and improved accuracy.

Usage:
    python train.py
    python train.py --data-path ../etl/db/data_clean/training_dataset.csv
"""

import argparse
import os
import sys
import joblib
import pandas as pd
import numpy as np

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import LabelEncoder

from modeling_related_files import TRAIN_TARGETS

# ── paths ──────────────────────────────────────────────────────────────────────
THIS_DIR   = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(THIS_DIR, "models")
os.makedirs(MODELS_DIR, exist_ok=True)

DROP_COLS     = ["budget", "is_synthetic", "data_source"]
IMPUTE_MEDIAN = ["engagement_score"]


# ──────────────────────────────────────────────────────────────────────────────
# 1. DATA LOADING
# ──────────────────────────────────────────────────────────────────────────────
import importlib.util

def _load_db_helpers():
    utils_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../etl/db/scripts/utils")
    )
    spec = importlib.util.spec_from_file_location(
        "db_helpers", os.path.join(utils_path, "db_helpers.py")
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def load_data(csv_path: str) -> pd.DataFrame:
    try:
        db = _load_db_helpers()
        conn = db.get_connection()
        query = """
            SELECT
                c.campaign_id,
                c.platform,
                c.budget,
                c.duration_days,
                c.campaign_intent,
                c.product_type,
                c.cta_type,
                a.age,
                a.gender,
                a.location,
                a.interests,
                a.audience_temperature,
                a.customer_type,
                a.career,
                cr.creative_type,
                cr.copy_text_length,
                cr.aspect_ratio,
                cr.visual_complexity,
                cr.has_person,
                p.ctr,
                p.conversion_rate,
                p.engagement_score,
                p.reach_score,
                p.lead_rate
            FROM campaigns c
            JOIN audience a ON a.campaign_id = c.campaign_id
            JOIN ads cr ON cr.campaign_id = c.campaign_id
            JOIN predictions p ON p.campaign_id = c.campaign_id
        """
        df = pd.read_sql(query, conn)
        conn.close()
        print(f"Loaded {len(df):,} rows from DB.")
        return df
    except Exception as e:
        print(f"DB unavailable ({e}), loading from CSV: {csv_path}")
        df = pd.read_csv(csv_path)
        print(f"Loaded {len(df):,} rows from CSV.")
        return df


# ──────────────────────────────────────────────────────────────────────────────
# 2. FEATURE ENGINEERING
# ──────────────────────────────────────────────────────────────────────────────
def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add derived features to improve signal."""
    df = df.copy()

    # Engagement efficiency: how much engagement per day
    if "engagement_score" in df.columns and "duration_days" in df.columns:
        df["engagement_per_day"] = df["engagement_score"] / (df["duration_days"] + 1)

    # Budget efficiency tiers (budget is dropped later but useful as ratio first)
    if "budget" in df.columns and "duration_days" in df.columns:
        df["budget_per_day"] = df["budget"] / (df["duration_days"] + 1)

    # Copy length bucket: short / medium / long
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


# ──────────────────────────────────────────────────────────────────────────────
# 3. PREPROCESSING
# ──────────────────────────────────────────────────────────────────────────────
def preprocess(df: pd.DataFrame, target: str):
    df = df.copy()

    # Drop bad rows — rows where conversion_rate=0 AND engagement_score=NaN
    # are incomplete synthetic records that add noise
    bad_rows = (df["conversion_rate"] == 0) & (df["engagement_score"].isnull())
    dropped  = bad_rows.sum()
    df = df[~bad_rows].reset_index(drop=True)
    print(f"Dropped {dropped:,} incomplete rows. Remaining: {len(df):,}")

    # Impute median
    for col in IMPUTE_MEDIAN:
        if col in df.columns:
            df[col] = df[col].fillna(df[col].median())

    # Drop metadata
    cols_to_drop = [c for c in DROP_COLS if c in df.columns]
    df = df.drop(columns=cols_to_drop)

    # Bin target into 3 tiers
    y_raw = df[target].copy()
    y = pd.qcut(y_raw, q=3, labels=["low", "medium", "high"]).astype(str)
    print(f"\nTier distribution for '{target}':\n{y.value_counts()}")

    # Drop all targets from X
    all_targets = ["ctr", "conversion_rate", "reach_score",
                   "engagement_score", "lead_rate"]
    cols_to_remove = [c for c in all_targets if c in df.columns and c != target]
    X = df.drop(columns=[target] + cols_to_remove)

    # Encode categoricals — do not use ``include=["str"]`` in ``select_dtypes``; it fails on
    # pandas StringDtype / recent pandas (use ``is_string_dtype`` instead).
    cat_cols = [
        c
        for c in X.columns
        if (
            pd.api.types.is_object_dtype(X[c])
            or pd.api.types.is_categorical_dtype(X[c])
            or pd.api.types.is_bool_dtype(X[c])
            or pd.api.types.is_string_dtype(X[c])
        )
    ]
    encoders = {}
    for col in cat_cols:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].astype(str))
        encoders[col] = le

    feature_cols = X.columns.tolist()
    print(f"Features used ({len(feature_cols)}): {feature_cols}")
    return X, y, feature_cols, encoders


# ──────────────────────────────────────────────────────────────────────────────
# 4. TRAINING
# ──────────────────────────────────────────────────────────────────────────────
def train(X_train, y_train):
    param_dist = {
        "n_estimators":      [200, 300],
        "max_depth":         [15, 20, None],
        "min_samples_leaf":  [3, 5, 10],
        "max_features":      ["sqrt", "log2"],
        "class_weight":      ["balanced", None],
    }

    search = RandomizedSearchCV(
        estimator           = RandomForestClassifier(random_state=42, n_jobs=-1),
        param_distributions = param_dist,
        n_iter              = 8,
        cv                  = 3,
        scoring             = "f1_macro",
        n_jobs              = -1,
        random_state        = 42,
        verbose             = 1,
    )

    print("\nRunning RandomizedSearchCV...")
    search.fit(X_train, y_train)
    print(f"Best params: {search.best_params_}")
    print(f"Best CV F1 (macro): {search.best_score_:.4f}")
    return search.best_estimator_


# ──────────────────────────────────────────────────────────────────────────────
# 5. EVALUATION
# ──────────────────────────────────────────────────────────────────────────────
def evaluate(model, X_test, y_test, label="Final Model"):
    preds = model.predict(X_test)
    acc   = accuracy_score(y_test, preds)
    print(f"\n{'─'*45}")
    print(f"  {label}")
    print(f"  Accuracy: {acc:.4f}")
    print(f"\n{classification_report(y_test, preds)}")
    print(f"{'─'*45}")


# ──────────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data-path",
        default=os.path.join(THIS_DIR, "../etl/db/data_clean/training_dataset.csv"),
    )
    args = parser.parse_args()

    df = load_data(args.data_path)
    df = engineer_features(df)

    for target in TRAIN_TARGETS:
        print(f"\n{'='*50}")
        print(f"  Training model for target: {target}")
        print(f"{'='*50}")

        X, y, feature_cols, encoders = preprocess(df, target)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        print(f"Train: {len(X_train):,}  Test: {len(X_test):,}")

        best_model = train(X_train, y_train)
        evaluate(best_model, X_test, y_test, label=f"RandomForest ({target})")

        joblib.dump(best_model,   os.path.join(MODELS_DIR, f"model_{target}.pkl"))
        joblib.dump(encoders,     os.path.join(MODELS_DIR, f"encoders_{target}.pkl"))
        joblib.dump(feature_cols, os.path.join(MODELS_DIR, f"feature_cols_{target}.pkl"))
        print(f"Saved model_{target}.pkl, encoders_{target}.pkl, feature_cols_{target}.pkl")

    print("\nAll models trained and saved.")