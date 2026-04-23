from pathlib import Path
import numpy as np
import pandas as pd

# -------------------------
# PATHS
# -------------------------
DB_ROOT = Path(__file__).resolve().parent.parent
DATA_RAW = DB_ROOT / "data_raw"
DATA_CLEAN = DB_ROOT / "data_clean"

RNG = np.random.default_rng(seed=42)

# -------------------------
# SYNTHETIC POOLS
# -------------------------
INTENTS = ["sales", "awareness", "traffic", "leads", "engagement"]
AUD_TEMPS = ["cold", "warm", "hot"]
CUST_TYPES = ["new", "returning"]
CTA_TYPES = ["buy_now", "learn_more", "sign_up", "go_to_page"]

PRODUCT_TYPES = ["electronics", "fashion", "food", "beauty", "fitness",
                 "finance", "travel", "education", "home", "software"]

CAREERS = ["student", "professional", "entrepreneur", "freelancer",
           "manager", "engineer", "teacher", "healthcare", "other"]

INTERESTS = ["tech", "fashion", "food", "sports", "travel",
             "music", "fitness", "finance", "gaming", "beauty"]

CREATIVE_TYPES = ["image", "video", "carousel", "story", "text"]
ASPECT_RATIOS = ["1:1", "4:5", "16:9", "9:16", "4:3"]

AGE_GROUPS = ["18-24", "25-34", "35-44", "45-54", "55+"]
LOCATIONS = ["US", "UK", "India", "Canada", "Germany", "France", "Armenia"]

# -------------------------
# SAFE COLUMN HELPER
# -------------------------
def safe_series(df, col):
    if col in df.columns:
        return df[col]
    return pd.Series(np.nan, index=df.index)

# -------------------------
# LOAD DATA
# -------------------------
def load_data():
    digital = pd.read_csv(DATA_RAW / "tech_advertising_campaigns_dataset.csv")
    marketing = pd.read_csv(DATA_RAW / "marketing_campaign_dataset.csv")

    print(f"[LOAD] digital: {digital.shape}")
    print(f"[LOAD] marketing: {marketing.shape}")

    return digital, marketing

# -------------------------
# CLEAN DIGITAL
# -------------------------
def clean_digital(df):
    df = df.drop_duplicates().copy()
    df.columns = [c.lower().strip().replace(" ", "_") for c in df.columns]

    df["platform"] = (
        df["ad_platform"].astype(str).str.lower()
        if "ad_platform" in df.columns
        else "facebook"
    )

    df["budget"] = pd.to_numeric(safe_series(df, "cost"), errors="coerce").fillna(500)
    df["clicks"] = pd.to_numeric(safe_series(df, "clicks"), errors="coerce").fillna(0)
    df["impressions"] = pd.to_numeric(safe_series(df, "impressions"), errors="coerce").fillna(1)
    df["conversion_rate"] = pd.to_numeric(safe_series(df, "conversion"), errors="coerce").fillna(0)

    df["ctr"] = (df["clicks"] / df["impressions"]).fillna(0)


    df["duration_days"] = RNG.integers(7, 60, len(df))

    df["data_source"] = "digital"
    df["is_synthetic"] = False

    return df

# -------------------------
# CLEAN MARKETING
# -------------------------
def clean_marketing(df):
    df = df.drop_duplicates().copy()
    df.columns = [c.lower().strip().replace(" ", "_") for c in df.columns]

    df["platform"] = (
        df["channel_used"].astype(str).str.lower()
        if "channel_used" in df.columns
        else "google"
    )

    df["budget"] = pd.to_numeric(safe_series(df, "acquisition_cost"), errors="coerce").fillna(500)
    df["clicks"] = pd.to_numeric(safe_series(df, "clicks"), errors="coerce").fillna(0)
    df["impressions"] = pd.to_numeric(safe_series(df, "impressions"), errors="coerce").fillna(1)
    df["conversion_rate"] = pd.to_numeric(safe_series(df, "conversion_rate"), errors="coerce").fillna(0)

    df["ctr"] = (df["clicks"] / df["impressions"]).fillna(0)

    df["engagement_score"] = pd.to_numeric(
        safe_series(df, "engagement_score"), errors="coerce"
    ).fillna(50)

    # ✅ IMPORTANT FIX
    df["duration_days"] = RNG.integers(7, 60, len(df))

    df["data_source"] = "marketing"
    df["is_synthetic"] = False

    return df

# -------------------------
# SYNTHETIC FEATURES
# -------------------------
def rand(pool, n):
    return RNG.choice(pool, size=n)

def add_synthetic(df):
    n = len(df)

    df["campaign_intent"] = rand(INTENTS, n)
    df["audience_temperature"] = rand(AUD_TEMPS, n)
    df["customer_type"] = rand(CUST_TYPES, n)
    df["cta_type"] = rand(CTA_TYPES, n)
    df["product_type"] = rand(PRODUCT_TYPES, n)
    df["career"] = rand(CAREERS, n)
    df["interests"] = rand(INTERESTS, n)

    df["creative_type"] = rand(CREATIVE_TYPES, n)
    df["aspect_ratio"] = rand(ASPECT_RATIOS, n)

    df["copy_text_length"] = RNG.integers(3, 40, n)
    df["visual_complexity"] = RNG.uniform(0.1, 0.9, n)
    df["has_person"] = RNG.choice([True, False], n)

    df["age"] = rand(AGE_GROUPS, n)
    df["gender"] = RNG.choice(["male", "female"], n)
    df["location"] = rand(LOCATIONS, n)

    return df

# -------------------------
# TARGETS
# -------------------------
def add_targets(df):
    n = len(df)

    if "engagement_score" not in df.columns:
        df["engagement_score"] = RNG.uniform(10, 90, n)

    df["reach_score"] = RNG.uniform(10, 100, n)
    df["lead_rate"] = (df["conversion_rate"] * 0.8).clip(0, 1)

    return df

# -------------------------
# FINAL COLUMNS (FIXED)
# -------------------------
FINAL_COLS = [
    "platform", "budget", "duration_days",
    "campaign_intent", "product_type", "cta_type",
    "age", "gender", "location", "interests",
    "audience_temperature", "customer_type", "career",
    "creative_type", "copy_text_length", "aspect_ratio",
    "visual_complexity", "has_person",
    "ctr", "conversion_rate", "engagement_score",
    "reach_score", "lead_rate",
    "data_source", "is_synthetic"
]

def finalize(df):
    return df[FINAL_COLS].copy()

# -------------------------
# SAVE
# -------------------------
def save(df):
    DATA_CLEAN.mkdir(parents=True, exist_ok=True)
    out = DATA_CLEAN / "training_dataset.csv"
    df.to_csv(out, index=False)
    print(f"[SAVE] {out} rows={len(df)} cols={df.shape[1]}")

# -------------------------
# PIPELINE
# -------------------------
def run_pipeline():
    digital, marketing = load_data()

    d = clean_digital(digital)
    m = clean_marketing(marketing)

    df = pd.concat([d, m], ignore_index=True)

    df = add_synthetic(df)
    df = add_targets(df)
    df = finalize(df)

    print("[DONE] pipeline complete:", df.shape)
    return df

if __name__ == "__main__":
    df = run_pipeline()
    save(df)