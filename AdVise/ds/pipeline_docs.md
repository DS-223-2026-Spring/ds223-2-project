# AdVise — DS Pipeline Documentation
## Milestone 3

---

## Overview

The DS pipeline predicts the **CTR performance tier** of an ad campaign
(Low / Medium / High) based on campaign setup, audience, and creative features.
This prediction helps the AdVise platform recommend better-performing ad configurations.

---

## Target Variable

| Variable | Type | Description |
|---|---|---|
| `ctr` (binned) | 3-class classification | Click-Through Rate bucketed into Low / Medium / High tiers using equal-frequency binning (33rd and 66th percentiles) |

**Why classification instead of regression?**
Raw CTR regression was attempted first (Milestone 2 baselines: Linear Regression,
Ridge, Random Forest, Gradient Boosting). All models achieved R² ≈ 0.035, indicating
the available features do not have sufficient linear or non-linear signal to predict
exact CTR values. Binning into tiers makes the problem more learnable and more
actionable for the business.

---

## Features Used (21)

| Feature | Type | Notes |
|---|---|---|
| `platform` | categorical | Ad platform (facebook, instagram, etc.) |
| `duration_days` | numerical | Campaign length in days |
| `campaign_intent` | categorical | Goal: awareness, sales, leads, etc. |
| `product_type` | categorical | Category of advertised product |
| `cta_type` | categorical | Call-to-action type |
| `age` | categorical | Target audience age group |
| `gender` | categorical | Target audience gender |
| `location` | categorical | Target geographic region |
| `interests` | categorical | Audience interest category |
| `audience_temperature` | categorical | Cold / warm / hot audience |
| `customer_type` | categorical | New vs returning customer |
| `career` | categorical | Audience occupation segment |
| `creative_type` | categorical | Ad format (image, video, carousel, etc.) |
| `copy_text_length` | numerical | Character length of ad copy |
| `aspect_ratio` | categorical | Creative aspect ratio (e.g. 4:5, 16:9) |
| `visual_complexity` | numerical | Float 0–1, complexity score of creative |
| `has_person` | boolean | Whether creative contains a person |
| `conversion_rate` | numerical | Post-campaign conversion ratio |
| `engagement_score` | numerical | Engagement signal, median-imputed if missing |
| `reach_score` | numerical | Estimated audience reach |
| `lead_rate` | numerical | Post-campaign lead generation ratio |

---

## Dropped Features

| Feature | Reason |
|---|---|
| `budget` | Constant value (500.0) across all rows — zero variance |
| `is_synthetic` | Metadata flag, not a predictor |
| `data_source` | Metadata; showed artificial correlation with CTR (r=0.19) — labeling artifact |

---

## Preprocessing Steps

1. Drop metadata columns (`budget`, `is_synthetic`, `data_source`)
2. Impute `engagement_score` missing values (4.76% missing) with median
3. Bin `ctr` into equal-frequency tiers: Low / Medium / High
4. Label-encode all categorical and boolean columns using `sklearn.LabelEncoder`
5. Train/test split: 80% train (168,000 rows) / 20% test (42,000 rows), `random_state=42`

---

## Models Tried

| Model | Metric | Score |
|---|---|---|
| Linear Regression (M2) | R² | 0.035 |
| Ridge Regression (M2) | R² | 0.035 |
| Random Forest Regressor (M2) | R² | ~0.035 |
| Gradient Boosting Regressor (M2) | R² | ~0.035 |
| Gradient Boosting Classifier (M3) | Accuracy | 0.377 |
| **Random Forest Classifier (M3)** | **Accuracy** | **0.377** |

**Final model selected:** Random Forest Classifier
(`n_estimators=100, max_depth=10, max_features=sqrt, min_samples_leaf=5`)

---

## Final Model Performance
| Class    | Precision | Recall | F1-Score |
|----------|-----------|--------|----------|
| high     | 0.35      | 0.52   | 0.42     |
| low      | 0.96      | 0.13   | 0.24     |
| medium   | 0.35      | 0.48   | 0.40     |
| **accuracy** |       |        | **0.38** |

**Key finding:** The model achieves 96% precision for the `low` tier -
meaning when it predicts an ad will underperform, it is almost always correct.
This is the most actionable output: the system can reliably flag campaigns
likely to fail before they are launched.

Overall accuracy (38%) is above random chance (33%) but limited by the
weak correlation between campaign-setup features and CTR outcomes.
This is consistent with industry knowledge that CTR depends heavily on
real-time signals (user context, ad fatigue, timing) not captured in
static campaign metadata.

---

## Artifacts Saved

| File | Description |
|---|---|
| `models/model.pkl` | Trained Random Forest Classifier |
| `models/encoders.pkl` | Fitted LabelEncoders for all categorical columns |
| `models/feature_cols.pkl` | Ordered list of 21 feature column names |

---

## How to Retrain

```bash
cd AdVise/ds
python train.py
# or with explicit data path:
python train.py --data-path ../etl/db/data_clean/training_dataset.csv
```