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
    FEATURE_COLS,
    DROP_COLS,
    IMPUTE_MEDIAN_COLS,
    TARGET,
)

# ── paths ──────────────────────────────────────────────────────────────────────
THIS_DIR    = os.path.dirname(os.path.abspath(__file__))
OUTPUTS_DIR = os.path.join(THIS_DIR, "outputs")
os.makedirs(OUTPUTS_DIR, exist_ok=True)


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
                c.id AS campaign_id,
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
# 2. PREDICT
# ──────────────────────────────────────────────────────────────────────────────
def run_predictions(df: pd.DataFrame, model, encoders: dict) -> pd.DataFrame:
    """
    Run model predictions and return a results dataframe with:
    - ctr_tier: predicted class (low / medium / high)
    - confidence_score: probability of the predicted class (0-1)
    - performance_segment: human-readable label for the business
    """
    # Keep campaign_id if it exists (from DB), for writing back
    id_col = df["campaign_id"] if "campaign_id" in df.columns else None

    # Keep actual CTR if available (for reference)
    actual_ctr = df[TARGET] if TARGET in df.columns else None

    # Preprocess
    X = preprocess_for_inference(df, encoders)

    # Predict class
    predicted_tier = model.predict(X)

    # Predict probabilities → confidence = max probability across classes
    proba = model.predict_proba(X)
    confidence = proba.max(axis=1).round(4)

    # Build results dataframe
    results = pd.DataFrame({
        "predicted_ctr_tier":  predicted_tier,
        "confidence_score":    confidence,
    })

    # Add actual CTR for reference if available
    if actual_ctr is not None:
        results.insert(0, "actual_ctr", actual_ctr.values)

    # Add campaign_id if available
    if id_col is not None:
        results.insert(0, "campaign_id", id_col.values)

    # Add performance segment — human readable label for the business
    segment_map = {
        "high":   "Strong Performer — recommend launching",
        "medium": "Average Performer — consider optimizing",
        "low":    "Weak Performer — do not recommend",
    }
    results["performance_segment"] = results["predicted_ctr_tier"].map(segment_map)

    return results


# ──────────────────────────────────────────────────────────────────────────────
# 3. SAVE TO CSV
# ──────────────────────────────────────────────────────────────────────────────
def save_to_csv(results: pd.DataFrame, output_path: str):
    results.to_csv(output_path, index=False)
    print(f"\nPredictions saved to: {output_path}")
    print(f"Total rows: {len(results):,}")
    print(f"\nTier distribution:")
    print(results["predicted_ctr_tier"].value_counts())
    print(f"\nSample output:")
    print(results.head(5).to_string(index=False))


# ──────────────────────────────────────────────────────────────────────────────
# 4. WRITE BACK TO DB
# ──────────────────────────────────────────────────────────────────────────────
def write_to_db(results: pd.DataFrame):
    """Write prediction results back to the predictions table in the DB."""
    try:
        sys.path.append(os.path.abspath("../etl/db/scripts/utils"))
        from db_helpers import get_connection

        conn = get_connection()
        cur  = conn.cursor()

        updated = 0
        for _, row in results.iterrows():
            if "campaign_id" not in row:
                continue
            cur.execute("""
                UPDATE predictions
                SET predicted_ctr_tier  = %s,
                    confidence_score    = %s,
                    performance_segment = %s
                WHERE campaign_id = %s
            """, (
                row["predicted_ctr_tier"],
                float(row["confidence_score"]),
                row["performance_segment"],
                int(row["campaign_id"]),
            ))
            updated += 1

        conn.commit()
        cur.close()
        conn.close()
        print(f"Written {updated:,} rows back to DB predictions table.")

    except Exception as e:
        print(f"DB write skipped ({e}). Results are saved in CSV only.")


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
    args = parser.parse_args()

    # 1. Load model artifacts
    print("Loading model artifacts...")
    model    = load_model()
    encoders = load_encoders()
    print("Model and encoders loaded.")

    # 2. Load data
    df = load_data(args.data_path)

    # 3. Predict
    print("\nRunning predictions...")
    results = run_predictions(df, model, encoders)

    # 4. Save to CSV
    save_to_csv(results, args.output_path)

    # 5. Try writing back to DB
    write_to_db(results)

    print("\nDone.")