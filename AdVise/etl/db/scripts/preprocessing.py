"""
Marketing / social preprocessing pipeline.
Place source CSVs under AdVise/etl/db/data_raw/ (see load_data() for expected filenames).
Output: AdVise/etl/db/data_clean/final_dataset.csv

Paths are resolved from this file, so the script works no matter the shell cwd.
"""
from pathlib import Path

import numpy as np
import pandas as pd

DB_ROOT = Path(__file__).resolve().parent.parent
DATA_RAW = DB_ROOT / "data_raw"
DATA_CLEAN = DB_ROOT / "data_clean"

# -------------------------
# LOAD DATA
# -------------------------
def load_data():
    social = pd.read_csv(DATA_RAW / "social_media_ad_optimization.csv")
    campaign = pd.read_csv(DATA_RAW / "marketing_campaign_dataset.csv")

    print("Social data shape:", social.shape)
    print("Campaign data shape:", campaign.shape)
    print("Social columns:", social.columns.tolist())

    return social, campaign


# -------------------------
# CLEAN DATA
# -------------------------
def clean_social(df):
    df = df.drop_duplicates()

    # Fix missing values (use correct column names)
    df["clicks"] = df["clicks"].fillna(0)
    df["impressions"] = df["impressions"].fillna(1)
    df["conversion"] = df["conversion"].fillna(0)

    return df


# -------------------------
# FEATURE ENGINEERING
# -------------------------
def add_metrics(df):
    # CTR
    df["CTR"] = df["clicks"] / df["impressions"]

    # Conversion rate
    df["conversion_rate"] = df["conversion"] / df["clicks"].replace(0, 1)

    return df


# -------------------------
# SYNTHETIC CAMPAIGN FEATURES
# -------------------------
def add_campaign_features(df):
    df["campaign_intent"] = np.random.choice(
        ["sales", "awareness", "traffic", "leads", "engagement"],
        size=len(df),
    )

    df["audience_temperature"] = np.random.choice(
        ["cold", "warm", "hot"],
        size=len(df),
    )

    df["customer_type"] = np.random.choice(
        ["new", "returning"],
        size=len(df),
    )

    df["cta_type"] = np.random.choice(
        ["buy_now", "learn_more", "sign_up"],
        size=len(df),
    )

    return df


# -------------------------
# BUSINESS METRICS (ROI)
# -------------------------
def add_business_metrics(df):
    # simulate cost (cost per impression)
    df["cost"] = df["impressions"] * 0.01

    # simulate revenue (per conversion)
    df["revenue"] = df["conversion"] * 5

    # ROI
    df["ROI"] = (df["revenue"] - df["cost"]) / df["cost"]

    return df


# -------------------------
# SAVE DATA
# -------------------------
def save(df):
    DATA_CLEAN.mkdir(parents=True, exist_ok=True)
    out = DATA_CLEAN / "final_dataset.csv"
    df.to_csv(out, index=False)
    print(f"Saved final dataset to {out}")


# -------------------------
# MAIN PIPELINE
# -------------------------
if __name__ == "__main__":
    social, _ = load_data()

    social = clean_social(social)
    social = add_metrics(social)
    social = add_campaign_features(social)
    social = add_business_metrics(social)

    save(social)
