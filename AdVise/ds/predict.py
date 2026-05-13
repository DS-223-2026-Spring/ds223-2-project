"""
predict.py
AdVise — Milestone 3
Runs predictions on campaign data and outputs results with confidence scores and segments.

Usage:
    python predict.py
    python predict.py --data-path ../etl/db/data_clean/training_dataset.csv
    python predict.py --output-path outputs/predictions.csv
"""

import argparse
import os
import sys
import pandas as pd
import numpy as np

from modeling_related_files import (
    load_model,
    load_encoders,
    preprocess_for_inference,
    engineer_features,
    DROP_COLS,
    IMPUTE_MEDIAN_COLS,
    TARGET,
    INTENT_TO_TARGET,
)

# ── paths ──────────────────────────────────────────────────────────────────────
THIS_DIR    = os.path.dirname(os.path.abspath(__file__))
OUTPUTS_DIR = os.path.join(THIS_DIR, "outputs")
os.makedirs(OUTPUTS_DIR, exist_ok=True)


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
                cr.ad_id,
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
                p.predicted_lead_rate AS lead_rate,
                p.predicted_engagement_score AS engagement_score
            FROM campaigns c
            JOIN audience a ON a.campaign_id = c.campaign_id
            JOIN ads cr ON cr.campaign_id = c.campaign_id
            LEFT JOIN predictions p ON p.campaign_id = c.campaign_id
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
# 2. PREDICT
# ──────────────────────────────────────────────────────────────────────────────
def run_predictions(df: pd.DataFrame, model, encoders: dict, target: str = "ctr") -> pd.DataFrame:
    """
    Run model predictions and return a results dataframe with:
    - ctr_tier: predicted class (low / medium / high)
    - confidence_score: probability of the predicted class (0-1)
    - performance_segment: human-readable label for the business
    """
    # Keep campaign_id if it exists (from DB), for writing back
    id_col = df["campaign_id"] if "campaign_id" in df.columns else None
    ad_id_col = df["ad_id"] if "ad_id" in df.columns else None

    # Keep actual CTR if available (for reference)
    actual_ctr = df[target] if target in df.columns else None

    # Preprocess
    X = preprocess_for_inference(df, encoders)

    # Predict class
    predicted_tier = model.predict(X)

    # Predict probabilities → confidence = max probability across classes
    proba = model.predict_proba(X)
    confidence = proba.max(axis=1).round(4)

    # Build results dataframe
    results = pd.DataFrame({
        f"predicted_{target}_tier": predicted_tier,
        "confidence_score": confidence,
    })
    if ad_id_col is not None:
        results.insert(0, "ad_id", ad_id_col.values)

    # Add actual CTR for reference if available
    if actual_ctr is not None:
        results.insert(0, f"actual_{target}", actual_ctr.values)

    # Add campaign_id if available
    if id_col is not None:
        results.insert(0, "campaign_id", id_col.values)

    # Add performance segment — human readable label for the business
    segment_map = {
        "high":   "Strong Performer — recommend launching",
        "medium": "Average Performer — consider optimizing",
        "low":    "Weak Performer — do not recommend",
    }
    results["performance_segment"] = results[f"predicted_{target}_tier"].map(segment_map)

    return results


# ──────────────────────────────────────────────────────────────────────────────
# 3. SAVE TO CSV
# ──────────────────────────────────────────────────────────────────────────────
def save_to_csv(results: pd.DataFrame, output_path: str):
    results.to_csv(output_path, index=False)
    print(f"\nPredictions saved to: {output_path}")
    print(f"Total rows: {len(results):,}")

    pred_cols = [c for c in results.columns if c.startswith("predicted_")]
    for col in pred_cols:
        print(f"\nDistribution for {col}:")
        print(results[col].value_counts())

    print(f"\nSample output:")
    print(results.head(5).to_string(index=False))


# ──────────────────────────────────────────────────────────────────────────────
# 4. WRITE BACK TO DB
# ──────────────────────────────────────────────────────────────────────────────
def write_to_db(results: pd.DataFrame):
    try:
        db = _load_db_helpers()
        conn = db.get_connection()
        cur = conn.cursor()
        inserted = 0
        for _, row in results.iterrows():
            if "campaign_id" not in row:
                continue
            target = row.get("target", "ctr")
            tier_col = f"predicted_{target}_tier"
            cur.execute("""
                INSERT INTO predictions
                    (campaign_id, ad_id, predicted_tier, predicted_metric, confidence_score)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (campaign_id, predicted_metric)
                DO UPDATE SET
                    predicted_tier = EXCLUDED.predicted_tier,
                    confidence_score = EXCLUDED.confidence_score
            """, (
                int(row["campaign_id"]),
                int(row["ad_id"]) if pd.notna(row.get("ad_id")) else None,
                row.get(tier_col),
                target,
                float(row["confidence_score"]),
            ))
            inserted += 1
        conn.commit()
        cur.close()
        conn.close()
        print(f"Inserted/updated {inserted:,} rows in predictions table.")
    except Exception as e:
        print(f"DB write skipped ({e}). Results saved in CSV only.")


# ──────────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data-path",
        default=os.path.join(THIS_DIR, "../etl/db/data_clean/training_dataset.csv"),
        help="Path to input CSV (fallback if DB is down)",
    )
    parser.add_argument(
        "--output-path",
        default=os.path.join(OUTPUTS_DIR, "predictions.csv"),
        help="Where to save the predictions CSV",
    )
    parser.add_argument(
        "--target",
        default=None,
        choices=["ctr", "conversion_rate", "reach_score"],
        help="Which target to predict. If not set, uses campaign_intent to decide.",
    )
    args = parser.parse_args()

    # 1. Load data
    df = load_data(args.data_path)

    df = engineer_features(df)

    # 2. Decide target per row based on campaign_intent (or use override)
    if args.target:
        # Single target forced by user
        targets_to_run = [args.target]
        df["_target"] = args.target
    else:
        # Map each row's campaign_intent to the right target
        df["_target"] = df["campaign_intent"].map(INTENT_TO_TARGET).fillna("ctr")
        targets_to_run = df["_target"].unique().tolist()

    all_results = []

    for target in targets_to_run:
        print(f"\nPredicting target: {target}")
        subset = df[df["_target"] == target].copy()

        model    = load_model(target)
        encoders = load_encoders(target)

        results = run_predictions(subset, model, encoders, target=target)
        results["target"] = target
        all_results.append(results)

    # 3. Combine and save
    final = pd.concat(all_results, ignore_index=True)
    save_to_csv(final, args.output_path)
    write_to_db(final)

    print("\nDone.")