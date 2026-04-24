"""
Load `data_clean/training_dataset.csv` into the offline `training_dataset` table only.

Live ERD tables (`campaigns`, `ads`, `audience`, `predictions`) are filled by the app/API, not here.
Run after: schema applied and `preprocessing.py` produced the CSV.
"""
from pathlib import Path
import os
import pandas as pd

from utils.db_utils import get_connection

# ----------------------------
# PATHS
# ----------------------------
DB_ROOT = Path(__file__).resolve().parent.parent
TRAINING_CSV = DB_ROOT / "data_clean" / "training_dataset.csv"


def main():
    df = pd.read_csv(TRAINING_CSV)
    print(f"[load_to_db] Dataset shape: {df.shape}")

    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("TRUNCATE TABLE training_dataset RESTART IDENTITY;")

        insert_sql = """
        INSERT INTO training_dataset (
            platform, budget, duration_days, campaign_intent, product_type, cta_type,
            age, gender, location, interests,
            audience_temperature, customer_type, career, creative_type,
            copy_text_length, aspect_ratio, visual_complexity, has_person,
            ctr, conversion_rate, engagement_score, reach_score,
            lead_rate, data_source, is_synthetic
        )
        VALUES (
            %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s,
            %s, %s, %s, %s,
            %s, %s, %s, %s,
            %s, %s, %s, %s,
            %s, %s, %s
        );
        """

        rows = []

        for _, row in df.iterrows():
            rows.append((
                row["platform"],
                float(row["budget"]) if pd.notna(row["budget"]) else None,
                int(row["duration_days"]) if pd.notna(row["duration_days"]) else None,
                row["campaign_intent"],
                row["product_type"],
                row["cta_type"],
                row["age"],
                row["gender"],
                row["location"],
                row["interests"],
                row["audience_temperature"],
                row["customer_type"],
                row["career"],
                row["creative_type"],
                int(row["copy_text_length"]) if pd.notna(row["copy_text_length"]) else None,
                row["aspect_ratio"],
                float(row["visual_complexity"]) if pd.notna(row["visual_complexity"]) else None,
                bool(row["has_person"]) if pd.notna(row["has_person"]) else False,
                float(row["ctr"]) if pd.notna(row["ctr"]) else None,
                float(row["conversion_rate"]) if pd.notna(row["conversion_rate"]) else None,
                float(row["engagement_score"]) if pd.notna(row["engagement_score"]) else None,
                float(row["reach_score"]) if pd.notna(row["reach_score"]) else None,
                float(row["lead_rate"]) if pd.notna(row["lead_rate"]) else None,
                row["data_source"],
                bool(row["is_synthetic"]) if pd.notna(row["is_synthetic"]) else False,
            ))

        cur.executemany(insert_sql, rows)
        conn.commit()

        print(f"[load_to_db] Inserted {len(rows)} rows")

    finally:
        cur.close()
        conn.close()

    db_name = os.environ.get("DB_NAME", "marketing_db")
    print(f"[DONE] Loaded into {db_name}")


if __name__ == "__main__":
    main()