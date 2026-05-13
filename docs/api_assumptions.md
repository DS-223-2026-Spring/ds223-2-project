# API assumptions and follow-ups

This page tracks **historical** notes and **optional** improvements; the primary contract is **OpenAPI** (`/openapi.json`) and **[API v1 examples](api/v1-endpoints.md)**.

## Implemented (current)

- **PostgreSQL** — **`/v1/campaigns/`**, **`/v1/ads/`**, **`/v1/audience/`**, **`/v1/predictions/`** use **`get_db`** and **`schema.sql`** tables.
- **Preview persistence** — **`POST /v1/predictions/preview`** with **`campaign_id`** + **`ad_id`** updates **`ads`**, upserts **`predictions`** on **`(campaign_id, predicted_metric)`**.
- **Joblib inference** — when artifacts exist under **`ADVISE_DS_MODELS`**, preview resolves tier from trained models (see **[DS models & inference](ds-models.md)**).
- **Legacy routes** — **`/campaigns`** (no **`v1`**) remain **in-memory** for demos; production UI should call **`/v1/*`**.

## Optional / product follow-ups

1. Remove or hide legacy non-**`v1`** routers if they confuse operators.
2. Harden **`training_dataset`** ↔ live **`campaign_id`** linkage for **`predict.py`** DB writes when batch-scoring offline rows.
3. Standardize error **`detail`** shapes across all routes (FastAPI default vs custom messages).
4. Pin **scikit-learn** across **`AdVise/api/requirements.txt`** and the DS training env to reduce pickle warnings.

## Pending confirmation (stakeholder)

- Long-term **auth** model for **`/v1/*`** (if any).
- **SLAs** and rate limits for preview + campaign create.
