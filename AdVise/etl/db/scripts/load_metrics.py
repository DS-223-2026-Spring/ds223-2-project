"""
Load engineered metrics from `data_clean/final_dataset.csv` into `campaign_metrics`.
`interaction_id` is taken as (row index + 1) and must match the order/IDs from `load_to_db.py` interactions.
Run after: load_to_db.py (same row order in CSV as interaction inserts).
"""
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
    conn = get_connection()
    cur = conn.cursor()
    try:
        for i, row in df.iterrows():
            cur.execute(
                """
                INSERT INTO campaign_metrics (
                    interaction_id, CTR, conversion_rate, campaign_intent,
                    audience_temperature, customer_type, cta_type,
                    cost, revenue, ROI
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
                (
                    i + 1,
                    row["CTR"],
                    row["conversion_rate"],
                    row["campaign_intent"],
                    row["audience_temperature"],
                    row["customer_type"],
                    row["cta_type"],
                    row["cost"],
                    row["revenue"],
                    row["ROI"],
                ),
            )
        conn.commit()
    finally:
        cur.close()
        conn.close()
    print("Metrics loaded into campaign_metrics")


if __name__ == "__main__":
    main()
