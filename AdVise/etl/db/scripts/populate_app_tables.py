import random
from collections import defaultdict

from utils.db_helpers import insert, get_connection

# -------------------------
# CAMPAIGNS
# -------------------------
def insert_campaigns(cur, n=20):
    campaign_ids = []

    for i in range(n):
        cid = insert(
            cur,
            "campaigns",
            [
                "campaign_name",
                "campaign_intent",
                "platform",
                "budget",
                "duration_days",
                "product_type",
                "cta_type",
            ],
            [
                f"Company_{i}",
                random.choice(["sales", "awareness", "traffic", "leads"]),
                random.choice(["facebook", "instagram", "google", "tiktok"]),
                round(random.uniform(500, 5000), 2),
                random.randint(7, 60),
                random.choice(
                    [
                        "beauty",
                        "education",
                        "electronics",
                        "fashion",
                        "finance",
                        "fitness",
                        "food",
                        "home",
                        "software",
                    ]
                ),
                random.choice(["buy_now", "learn_more", "sign_up", "go_to_page"]),
            ],
            returning="campaign_id"
        )

        campaign_ids.append(cid)

    return campaign_ids


# -------------------------
# ADS
# -------------------------
def insert_ads(cur, campaign_ids):
    """Return (campaign_id, ad_id) pairs so predictions can reference a valid ad per campaign."""
    pairs = []

    for cid in campaign_ids:
        for _ in range(random.randint(1, 3)):

            aid = insert(
                cur,
                "ads",
                [
                    "campaign_id",
                    "creative_type",
                    "cta_type",
                    "copy_text_length",
                    "aspect_ratio",
                    "visual_complexity",
                    "has_person",
                    "creative_url"
                ],
                [
                    cid,
                    random.choice(["image", "video", "carousel", "story"]),
                    random.choice(["buy_now", "learn_more", "sign_up", "go_to_page"]),
                    random.randint(5, 50),
                    random.choice(["1:1", "4:5", "16:9", "9:16"]),
                    round(random.uniform(0.1, 0.9), 3),
                    random.choice([True, False]),
                    f"https://ads.example.com/ad_{random.randint(1000,9999)}"
                ],
                returning="ad_id"
            )

            pairs.append((cid, aid))

    return pairs


# -------------------------
# AUDIENCE
# -------------------------
def insert_audience(cur, campaign_ids):
    for cid in campaign_ids:
        insert(
            cur,
            "audience",
            [
                "campaign_id",
                "age",
                "gender",
                "location",
                "interests",
                "audience_temperature",
                "customer_type",
                "career"
            ],
            [
                cid,
                random.choice(["18-24", "25-34", "35-44", "45-54"]),
                random.choice(["male", "female"]),
                random.choice(["US", "UK", "India", "Armenia", "Germany"]),
                random.choice(["tech", "fashion", "sports", "music", "food"]),
                random.choice(["cold", "warm", "hot"]),
                random.choice(["new", "returning"]),
                random.choice(["student", "professional", "teacher", "engineer", "other"])
            ]
        )


# -------------------------
# PREDICTIONS
# -------------------------
# Matches ``uq_campaign_metric``: one row per (campaign_id, predicted_metric).
_METRICS = ("ctr", "conversion_rate", "reach_score")


def insert_predictions(cur, campaign_ad_pairs):
    by_campaign = defaultdict(list)
    for cid, aid in campaign_ad_pairs:
        by_campaign[cid].append(aid)

    for cid, aids in by_campaign.items():
        for metric in _METRICS:
            insert(
                cur,
                "predictions",
                [
                    "campaign_id",
                    "ad_id",
                    "predicted_metric",
                    "predicted_tier",
                    "confidence",
                ],
                [
                    cid,
                    random.choice(aids),
                    metric,
                    random.choice(["low", "medium", "high"]),
                    round(random.uniform(0.35, 0.95), 4),
                ],
            )


# -------------------------
# MAIN
# -------------------------
def main():
    conn = get_connection()
    cur = conn.cursor()

    try:
        print("[START] inserting synthetic app data...")

        campaign_ids = insert_campaigns(cur)
        campaign_ad_pairs = insert_ads(cur, campaign_ids)

        insert_audience(cur, campaign_ids)
        insert_predictions(cur, campaign_ad_pairs)

        conn.commit()
        print("[DONE] synthetic data inserted successfully")

    except Exception as e:
        conn.rollback()
        print("[ERROR]", e)

    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()