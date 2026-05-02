"""
train.py
AdVise — Milestone 3
Final model training script. Run this to train, evaluate, and save the model.

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

from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.model_selection import train_test_split, RandomizedSearchCV, cross_val_score
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.metrics import classification_report, accuracy_score
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler

# ── paths ──────────────────────────────────────────────────────────────────────
THIS_DIR   = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(THIS_DIR, "models")
os.makedirs(MODELS_DIR, exist_ok=True)

# ── constants ──────────────────────────────────────────────────────────────────
TARGET        = "ctr"
DROP_COLS     = ["budget", "is_synthetic", "data_source"]
IMPUTE_MEDIAN = ["engagement_score"]


# ──────────────────────────────────────────────────────────────────────────────
# 1. DATA LOADING
# ──────────────────────────────────────────────────────────────────────────────
def load_data(csv_path: str) -> pd.DataFrame:
    """Load data from DB; fall back to CSV if DB is unavailable."""
    try:
        sys.path.append(os.path.abspath("../etl/db/scripts/utils"))
        from db_helpers import get_connection

        conn = get_connection()
        query = """
            SELECT
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
            JOIN audience a    ON a.campaign_id = c.id
            JOIN ads cr        ON cr.campaign_id = c.id
            JOIN predictions p ON p.campaign_id  = c.id
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
# 2. PREPROCESSING
# ──────────────────────────────────────────────────────────────────────────────
def preprocess(df: pd.DataFrame):
    """
    Clean, impute, encode.
    Returns X, y, list of feature column names, and dict of fitted encoders.
    """
    df = df.copy()

    # Drop constant / metadata columns that exist
    cols_to_drop = [c for c in DROP_COLS if c in df.columns]
    df = df.drop(columns=cols_to_drop)

    # Impute with median
    for col in IMPUTE_MEDIAN:
        if col in df.columns:
            df[col] = df[col].fillna(df[col].median())

    # Bin CTR into 3 performance tiers BEFORE separating X
    y_raw = df[TARGET].copy()
    y = pd.qcut(y_raw, q=3, labels=["low", "medium", "high"])
    y = y.astype(str)
    print(f"\nCTR tier distribution:\n{y.value_counts()}")

    # NOW separate X (after y is done)
    X = df.drop(columns=[TARGET])

    # Encode categoricals + booleans
    cat_cols = X.select_dtypes(include=["object", "bool", "str"]).columns.tolist()
    encoders = {}
    for col in cat_cols:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].astype(str))
        encoders[col] = le

    feature_cols = X.columns.tolist()
    print(f"Features used ({len(feature_cols)}): {feature_cols}")
    return X, y, feature_cols, encoders


# ──────────────────────────────────────────────────────────────────────────────
# 3. TRAINING + TUNING
# ──────────────────────────────────────────────────────────────────────────────
def train(X_train, y_train):
    """
    Run RandomizedSearchCV over RandomForestClassifier.
    Returns the best fitted estimator.
    """
    from sklearn.ensemble import RandomForestClassifier

    param_dist = {
        "n_estimators":  [100, 200],
        "max_depth":     [10, 20, None],
        "min_samples_leaf": [5, 10],
        "max_features":  ["sqrt", "log2"],
    }

    base = RandomForestClassifier(random_state=42, n_jobs=-1)

    search = RandomizedSearchCV(
        estimator           = base,
        param_distributions = param_dist,
        n_iter              = 5,
        cv                  = 2,
        scoring             = "accuracy",
        n_jobs              = -1,
        random_state        = 42,
        verbose             = 2,
    )

    print("\nRunning RandomizedSearchCV...")
    search.fit(X_train, y_train)

    print(f"\nBest params: {search.best_params_}")
    print(f"Best CV Accuracy: {search.best_score_:.4f}")
    return search.best_estimator_


# ──────────────────────────────────────────────────────────────────────────────
# 4. EVALUATION
# ──────────────────────────────────────────────────────────────────────────────
def evaluate(model, X_test, y_test, label="Final Model"):
    preds = model.predict(X_test)
    acc   = accuracy_score(y_test, preds)
    print(f"\n{'─'*45}")
    print(f"  {label}")
    print(f"  Accuracy: {acc:.4f}")
    print(f"\n{classification_report(y_test, preds)}")
    print(f"{'─'*45}")
    return preds, acc


# ──────────────────────────────────────────────────────────────────────────────
# 5. SAVE
# ──────────────────────────────────────────────────────────────────────────────
def save_artifacts(model, encoders, feature_cols):
    joblib.dump(model,        os.path.join(MODELS_DIR, "model.pkl"))
    joblib.dump(encoders,     os.path.join(MODELS_DIR, "encoders.pkl"))
    joblib.dump(feature_cols, os.path.join(MODELS_DIR, "feature_cols.pkl"))
    print(f"\nSaved to {MODELS_DIR}/")
    print("  model.pkl")
    print("  encoders.pkl")
    print("  feature_cols.pkl")


# ──────────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data-path",
        default=os.path.join(THIS_DIR, "../etl/db/data_clean/training_dataset.csv"),
        help="Path to training CSV (fallback if DB is down)",
    )
    args = parser.parse_args()

    # 1. Load
    df = load_data(args.data_path)

    # 2. Preprocess
    X, y, feature_cols, encoders = preprocess(df)

    # 3. Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    print(f"\nTrain size: {len(X_train):,}   Test size: {len(X_test):,}")

    # 4. Train
    best_model = train(X_train, y_train)

    # 5. Evaluate
    evaluate(best_model, X_test, y_test, label="RandomForest (tuned)")

    # 6. Save
    save_artifacts(best_model, encoders, feature_cols)

    print("\nDone. Model is ready.")