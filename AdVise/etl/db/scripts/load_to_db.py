"""
Load `data_clean/final_dataset.csv` into users, ads, and interactions.
Run after: DB exists, schema applied, preprocessing produced the CSV.
"""
import os
import sys
from pathlib import Path

import pandas as pd

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from utils.db_utils import get_connection  # noqa: E402

DB_ROOT = Path(__file__).resolve().parent.parent
FINAL_CSV = DB_ROOT / "data_clean" / "final_dataset.csv"


def main() -> None:
    df = pd.read_csv(FINAL_CSV)
    print("Dataset shape:", df.shape)

    conn = get_connection()
    cur = conn.cursor()
    try:
        # Full reload: safe when compose runs ETL on every up (keeps interaction_id 1..N for load_metrics).
        cur.execute(
            "TRUNCATE campaign_metrics, interactions, users, ads RESTART IDENTITY;"
        )
        # -----------------------------
        # USERS TABLE
        # -----------------------------
        users = df[
            ["user_id", "age", "gender", "location", "interests", "device_type"]
        ].drop_duplicates()
        for _, row in users.iterrows():
            cur.execute(
                """
                INSERT INTO users (user_id, age, gender, location, interests, device_type)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (user_id) DO NOTHING;
            """,
                tuple(row),
            )
        print("Users inserted (or skipped on conflict)")

        # -----------------------------
        # ADS TABLE
        # -----------------------------
        ads = df[["ad_id", "ad_category", "ad_platform", "ad_type"]].drop_duplicates()
        for _, row in ads.iterrows():
            cur.execute(
                """
                INSERT INTO ads (ad_id, ad_category, ad_platform, ad_type)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (ad_id) DO NOTHING;
            """,
                tuple(row),
            )
        print("Ads inserted (or skipped on conflict)")

        # -----------------------------
        # INTERACTIONS TABLE
        # -----------------------------
        for _, row in df.iterrows():
            cur.execute(
                """
                INSERT INTO interactions (
                    user_id, ad_id, impressions, clicks, conversion,
                    time_spent_on_ad, day_of_week, engagement_score
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """,
                (
                    row["user_id"],
                    row["ad_id"],
                    row["impressions"],
                    row["clicks"],
                    row["conversion"],
                    row["time_spent_on_ad"],
                    row["day_of_week"],
                    row["engagement_score"],
                ),
            )
        print("Interactions inserted")
        conn.commit()
    finally:
        cur.close()
        conn.close()
    _db = os.environ.get("DB_NAME") or os.environ.get("MARKETING_DB_NAME") or "marketing_db"
    print(f"DONE: data loaded into PostgreSQL ({_db})")


if __name__ == "__main__":
    main()
