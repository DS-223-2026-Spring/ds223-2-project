import random
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
                "company",
                "campaign_type",
                "platform",
                "budget",
                "duration_days",
                "start_date",
                "campaign_intent",
                "product_type",
                "cta_type",
                "discount_offered",
                "season_month"
            ],
            [
                f"Company_{i}",
                random.choice(["sales", "awareness", "traffic", "leads"]),
                random.choice(["facebook", "instagram", "google", "tiktok"]),
                round(random.uniform(500, 5000), 2),
                random.randint(7, 60),
                "2025-01-01",
                random.choice(["intent_a", "intent_b", "intent_c"]),
                random.choice(["electronics", "fashion", "food", "home"]),
                random.choice(["buy_now", "learn_more", "sign_up"]),
                random.choice(["10%", "20%", "none"]),
                random.choice(["Jan", "Feb", "Mar", "Apr"])
            ],
            returning="campaign_id"
        )

        campaign_ids.append(cid)

    return campaign_ids


# -------------------------
# ADS
# -------------------------
def insert_ads(cur, campaign_ids):
    ad_ids = []

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
                    random.choice(["buy_now", "learn_more", "sign_up"]),
                    random.randint(5, 50),
                    random.choice(["1:1", "4:5", "16:9", "9:16"]),
                    round(random.uniform(0.1, 0.9), 3),
                    random.choice([True, False]),
                    f"https://ads.example.com/ad_{random.randint(1000,9999)}"
                ],
                returning="ad_id"
            )

            ad_ids.append(aid)

    return ad_ids


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
def insert_predictions(cur, campaign_ids, ad_ids):
    for i in range(min(len(campaign_ids), len(ad_ids))):
        insert(
            cur,
            "predictions",
            [
                "campaign_id",
                "ad_id",
                "predicted_ctr",
                "predicted_conversion_rate",
                "predicted_engagement_score",
                "predicted_reach_score",
                "predicted_lead_rate",
                "predicted_metric"
            ],
            [
                campaign_ids[i],
                ad_ids[i],
                round(random.uniform(0.01, 0.25), 4),
                round(random.uniform(0.001, 0.1), 4),
                round(random.uniform(10, 90), 2),
                round(random.uniform(10, 100), 2),
                round(random.uniform(0.0, 0.5), 4),
                random.choice(["CTR", "CONVERSION", "ENGAGEMENT", "REACH"])
            ]
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
        ad_ids = insert_ads(cur, campaign_ids)

        insert_audience(cur, campaign_ids)
        insert_predictions(cur, campaign_ids, ad_ids)

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