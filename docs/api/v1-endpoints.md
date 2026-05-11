# HTTP API v1 — request/response examples

Base URL examples:

| Context | URL |
|---------|-----|
| Docker Compose (host machine) | `http://localhost:8008` |
| Streamlit container → API | `http://back:8000` |

OpenAPI (`/openapi.json`) and Swagger UI (`/docs`) are the authoritative machine-readable contract. These examples mirror `AdVise/api/schema.py` (`StatusResponse`, `MetaEnumsResponse`, `PredictionPreviewRequest`, `PredictionPreviewResponse`).

---

## `GET /v1/status`

**Response `200`** — `application/json`:

```json
{
  "status": "ok",
  "backend": "connected",
  "model_version": "v1-placeholder",
  "max_creatives": 3,
  "upload_limits": {
    "max_file_size_mb": 10,
    "allowed_types": ["png", "jpg", "jpeg", "pdf"]
  },
  "prefect_available": false
}
```

Set environment variable **`ADVISE_PREFECT_AVAILABLE=true`** on the API service if a Prefect worker for creative extraction is reachable; the field is exposed for UX only.

---

## `GET /v1/meta/enums`

**Response `200`** — matches `MetaEnumsResponse`. Values are **`DISTINCT` queries** on
`training_dataset` (platform, campaign_intent, product_type, cta_type, audience_temperature,
customer_type, location → `regions`, age → `age_bands`) so dropdowns match model training
vocabulary. If a column is empty, the API falls back to static pools aligned with
`AdVise/etl/db/scripts/preprocessing.py`. **`devices`** has no DB column and stays a small static list.

Example shape (your rows will differ):

```json
{
  "platforms": ["facebook", "google", "instagram", "tiktok", "youtube"],
  "campaign_intents": ["awareness", "engagement", "leads", "sales", "traffic"],
  "cta_types": ["buy_now", "go_to_page", "learn_more", "sign_up"],
  "audience_temperature": ["cold", "hot", "warm"],
  "devices": ["mobile", "desktop", "tablet"],
  "customer_types": ["new", "returning"],
  "product_types": ["beauty", "electronics", "fashion", "food", "software"],
  "regions": ["Armenia", "Canada", "France", "Germany", "India", "UK", "US"],
  "age_bands": ["18-24", "25-34", "35-44", "45-54", "55+"]
}
```

Frontend must use key **`audience_temperature`** (not `audience_temperatures`).

---

## `POST /v1/predictions/preview`

**Request** — `application/json` (`PredictionPreviewRequest`):

```json
{
  "platform": "instagram",
  "campaign_intent": "awareness",
  "product_type": "software",
  "cta_type": "learn_more",
  "audience_temperature": "cold",
  "customer_type": "new",
  "budget": 5000,
  "duration_days": 14,
  "creative_count": 2,
  "creative_image_base64": "<optional standard base64 of first image; API runs creative_extract>"
}
```

`creative_count` is optional (default `1`); capped in logic for alternate recommendation rows.
Optional **`audience_age`**, **`audience_gender`**, **`audience_location`**, **`audience_interests`**, **`career`** override inference defaults.

**Response `200`** — `PredictionPreviewResponse` (shape illustrative; IDs and tiers vary):

```json
{
  "run_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "status": "success",
  "model_version": "v1-intent-mapping",
  "campaign_intent": "awareness",
  "target_metric": "reach_score",
  "target_label": "Predicted reach tier (awareness)",
  "predicted_tier": "medium",
  "prediction_confidence": 0.55,
  "recommendations": [
    {
      "rank": 1,
      "primary_kpi": "reach_score",
      "score": 0.55,
      "hint": "Placeholder tier for `reach_score` (`awareness`). Mount `./AdVise/ds/models` → `/api/ds_models` and install sklearn/joblib for live tier inference."
    }
  ],
  "input_summary": {
    "platform": "Instagram",
    "campaign_intent": "awareness",
    "product_type": "software",
    "cta_type": "Learn More",
    "audience_temperature": "cold",
    "customer_type": "new",
    "budget": 5000,
    "duration_days": 14,
    "creative_count": 2
  }
}
```

**Single outcome per preview:** `campaign_intent` resolves to **exactly one** `target_metric` + `target_label`. The API trains and loads **one** classifier bundle per metric; a preview call scores **only** that metric—not CTR, conversion, and reach at once. Canonical mapping lives in **`AdVise/api/campaign_intent.py`** (`INTENT_TO_TARGET_METRIC`):

| Campaign intent (normalized, lowercase) | `target_metric` |
|----------------------------------------|-----------------|
| `awareness` | `reach_score` |
| `traffic`, `engagement` | `ctr` |
| `sales`, `leads`, `conversion`, `lead_generation` | `conversion_rate` |
| unknown / other | defaults to `ctr` |

**Creative features:** pass **`creative_image_base64`** (first image). The API decodes a temp file and runs **`creative_prefect.extract_creative_for_preview`**, which executes the Prefect flow **`api-creative-extraction-preview`** (with retries). Set **`ADVISE_SKIP_PREFECT_CREATIVE=1`** on **`back`** to bypass Prefect. **`creative_extract`** is mounted at `/api/creative_extract.py` in Compose. Without an image, preview uses stub creative fields. Tier scoring uses joblib models under **`AdVise/ds/models`** (`train.py`; legacy **`model.pkl`** only for **`ctr`** unless **`ADVISE_LEGACY_MODEL_ONLY_FOR`** is set). **`outputs/predictions.csv`** is offline-only.

---

## `GET /v1/prediction-runs/{run_id}`

Returns the stored preview result for a `run_id` issued by `POST /v1/predictions/preview`. Storage is **in-memory** on the API process (`prediction_runs` dict); restarting the container clears it.

**Response `200`** when found — same schema as preview (`PredictionRunResponse`).

When missing:

```json
{
  "run_id": "...",
  "status": "failed",
  "model_version": "v1-intent-mapping",
  "campaign_intent": "",
  "target_metric": "ctr",
  "target_label": "",
  "predicted_tier": null,
  "prediction_confidence": null,
  "recommendations": [],
  "input_summary": {}
}
```

---

## Read-only `/v1/*` listings (PostgreSQL)

These return JSON objects built from SQL; response shapes follow live columns in `schema.sql`. Example campaign list excerpt:

### `GET /v1/campaigns/`

```json
{
  "count": 2,
  "campaigns": [
    {
      "campaign_id": 1,
      "company": "...",
      "campaign_type": null,
      "platform": "Instagram",
      "budget": 500.0,
      "duration_days": 7,
      "start_date": null,
      "campaign_intent": "awareness",
      "product_type": "software"
    }
  ]
}
```

Analogous prefixes: **`/v1/ads/`**, **`/v1/audience/`**, **`/v1/predictions/`** (see OpenAPI tags).
