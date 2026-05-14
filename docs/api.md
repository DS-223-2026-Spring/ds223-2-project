# API — FastAPI backend

The product brain of AdVise. A FastAPI service exposed on host port **8008** that:

- Persists campaigns, audiences, ads, and predictions in PostgreSQL.
- Serves a typed `/v1` REST API (Swagger UI at `/docs`, ReDoc at `/redoc`).
- Runs **live tier inference** by loading the trained joblib models (`AdVise/ds/models/*.pkl`).
- Optionally extracts creative features through a Prefect-wrapped flow when a base64 image is supplied.

Source: `AdVise/api/`.

## Layout

```
AdVise/api/
├── main.py              # FastAPI app, lifespan, mounted routers, /openapi.json
├── schema.py            # Pydantic request/response schemas (PredictionPreviewRequest, ...)
├── models.py            # SQLAlchemy ORM models mirroring schema.sql
├── database.py          # Engine + get_db() dependency
├── campaign_intent.py   # INTENT_TO_TARGET_METRIC mapping
├── prediction_models.py # Joblib loader + tier inference
├── creative_prefect.py  # Prefect flow for image-based creative extraction
└── routes/
    ├── campaigns_v1.py      # /v1/campaigns/  (CRUD via Postgres)
    ├── ads_v1.py            # /v1/ads/
    ├── audience_v1.py       # /v1/audience/
    ├── predictions_v1.py    # /v1/predictions/ (listings)
    ├── predictions_preview.py # POST /v1/predictions/preview, GET /v1/prediction-runs/{id}
    ├── meta.py              # GET /v1/meta/enums
    ├── route2.py            # GET /v1/status
    ├── campaigns.py / ads.py / audience.py / predictions.py  # Legacy in-memory demos
    └── training_dataset.py / routen.py                        # Aux training-data inspection
```

The entry point and routers:

::: api.main

## Route groups

| Prefix | Source | Notes |
|--------|--------|-------|
| **`/v1/campaigns/`**, **`/v1/ads/`**, **`/v1/audience/`**, **`/v1/predictions/`** | `routes/campaigns_v1.py`, `ads_v1.py`, `audience_v1.py`, `predictions_v1.py` | PostgreSQL via `get_db`. **Primary product API.** |
| **`POST /v1/predictions/preview`**, **`GET /v1/prediction-runs/{run_id}`** | `routes/predictions_preview.py` | Live preview; optional DB upsert into `ads` / `predictions`. |
| **`GET /v1/status`**, **`GET /v1/meta/enums`** | `routes/route2.py`, `routes/meta.py` | Health + enum vocabulary (DB-backed where columns exist). |
| `/campaigns`, `/ads`, ... (no `v1` prefix) | `routes/campaigns.py`, etc. | **Legacy in-memory** demos — keep around for tutorials; production UI should always call `/v1/*`. |
| `/training_dataset`, `/ext`, core `/route2` | `routen.py`, `training_dataset.py` | Training-data sampling / extensions. |

OpenAPI: **`/openapi.json`**. Swagger UI: **`/docs`**. ReDoc: **`/redoc`**.

## SQLAlchemy models — `models.py`

Mirror the live tables in `AdVise/etl/db/sql/schema.sql` (see [Database ERD](erd.md)). Used by every `/v1/*` route through `database.get_db`.

::: api.models
    options:
        show_source: true

## `/v1` endpoints — request/response examples

Base URLs:

| Context | URL |
|---------|-----|
| Docker Compose (host machine) | `http://localhost:8008` |
| Streamlit container → API | `http://back:8000` |

The canonical machine-readable contract is `/openapi.json`. The examples below mirror `AdVise/api/schema.py`.

### `GET /v1/status`

**Response `200`**:

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
  "prefect_available": true
}
```

In the default Compose stack `ADVISE_PREFECT_AVAILABLE=true` is set on `back`, so `prefect_available` is `true`. Override in `.env` to bypass Prefect (the field is UX-only and affects the creative-extraction wiring only).

### `GET /v1/meta/enums`

Returns the dropdown vocabulary that the Streamlit form should use. Values come from `DISTINCT` queries on `training_dataset` so the UI vocabulary matches what the model was trained on. Columns that are empty fall back to static pools aligned with `AdVise/etl/db/scripts/preprocessing.py`. The `devices` field has no DB column and is always a small static list.

Example (your live values will differ):

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
  "age_bands": ["18-24", "25-34", "35-44", "45-54", "55+"],
  "genders": ["male", "female"],
  "interests": ["beauty", "fashion", "finance", "food", "tech"],
  "careers": ["engineer", "manager", "professional", "student", "teacher"]
}
```

Frontend must use key **`audience_temperature`** (singular, not `audience_temperatures`).

### `POST /v1/predictions/preview`

The product's headline endpoint. Returns exactly **one** tier prediction on the metric that matches the campaign's intent (see "Single outcome per preview" below).

**Request** (`PredictionPreviewRequest`):

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
  "audience_age": "25-34",
  "audience_gender": "female",
  "audience_location": "US",
  "audience_interests": "tech",
  "career": "professional",
  "campaign_id": 12,
  "ad_id": 34,
  "creative_image_base64": "<optional base64 image; API runs creative_extract>",
  "creative_asset_url": "https://cdn.example.com/creative.jpg"
}
```

- `creative_count` is optional (default `1`); capped server-side for alternate recommendation rows.
- The audience fields (`audience_age`, `audience_gender`, `audience_location`, `audience_interests`, `career`) override inference defaults when sent. The Streamlit Campaign Input page sources their dropdown values from `GET /v1/meta/enums`.
- `creative_asset_url` sets `ads.creative_url` when persisting. Omit or leave blank to keep the URL already stored for that ad.
- Send `campaign_id` **and** `ad_id` together (e.g. from a prior `POST /v1/campaigns/`) to **update** the matching `ads` row with extracted creative fields **and upsert** the `predictions` row on `(campaign_id, predicted_metric)`. Omit both to skip DB persistence (preview-only). Sending only one of the two returns **422**.

**Response `200`** (`PredictionPreviewResponse`):

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
  "prediction_id": 901,
  "recommendations": [
    {
      "rank": 1,
      "primary_kpi": "reach_score",
      "score": 0.55,
      "hint": "Mount `./AdVise/ds/models` → `/api/ds_models` for live tier inference."
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

#### Single outcome per preview

`campaign_intent` resolves to **exactly one** `target_metric` + `target_label`. The API loads **one** classifier bundle per metric; a preview scores **only** that metric — **not** CTR, conversion, and reach at once. Canonical mapping in `AdVise/api/campaign_intent.py` (`INTENT_TO_TARGET_METRIC`):

| Campaign intent (normalized) | `target_metric` |
|------------------------------|-----------------|
| `awareness` | `reach_score` |
| `traffic`, `engagement` | `ctr` |
| `sales`, `leads`, `conversion`, `lead_generation` | `conversion_rate` |
| unknown / other | `ctr` (default) |

See [Data Science](ds-models.md) for the model behind each metric.

#### Creative features

Pass `creative_image_base64` (first image only). The API decodes a temp file and runs `creative_prefect.extract_creative_for_preview`, which executes the Prefect flow `api-creative-extraction-preview` (with retries). Set `ADVISE_SKIP_PREFECT_CREATIVE=1` on `back` to bypass Prefect for debugging. Without an image, preview falls back to stub creative fields. See [Orchestration](orchestration.md) for the flow details.

Tier scoring uses the joblib models under `AdVise/ds/models` (mounted at `/api/ds_models` on `back`). The legacy `model.pkl` is used only for `ctr` unless `ADVISE_LEGACY_MODEL_ONLY_FOR` is set.

### `GET /v1/prediction-runs/{run_id}`

Returns the stored preview result for a `run_id` issued by `POST /v1/predictions/preview`. Storage is **in-memory** on the API process (`prediction_runs` dict); restarting the container clears it.

`200` with the same shape as a preview response, or `200` with `status: "failed"` and empty fields when missing.

### PostgreSQL-backed listings and create

`GET /v1/campaigns/` returns a count + list of `campaigns` rows. Example:

```json
{
  "count": 2,
  "campaigns": [
    {
      "campaign_id": 1,
      "campaign_name": "Spring push",
      "campaign_intent": "awareness",
      "platform": "instagram",
      "budget": 500.0,
      "duration_days": 7,
      "product_type": "software",
      "cta_type": "learn_more",
      "created_at": "2026-01-15T12:00:00"
    }
  ]
}
```

`POST /v1/campaigns/` (`CampaignCreateRequest`) inserts **one** `campaigns` row and **one** `audience` row in a **single transaction** (rollback if either fails). Body includes campaign fields (`campaign_name`, `campaign_intent`, `platform`, `budget`, `duration_days`, `product_type`, `cta_type`) plus audience fields aligned with the `audience` table / preview API (`audience_age`, `audience_gender`, `audience_location`, `audience_interests`, `audience_temperature`, `customer_type`, `career`). The response includes `campaign_id`, `audience_id`, and the campaign columns returned from `RETURNING`.

Analogous prefixes: `/v1/ads/`, `/v1/audience/`, `/v1/predictions/`. See OpenAPI tags for the full surface.

## Refreshing `openapi.json`

The Swagger UI at `/docs` is generated live, but a checked-in `docs/api/openapi.json` is also produced for offline consumption. Refresh it with:

```bash
# Offline export (no DB required — sets SKIP_DB_VERIFY=1)
python3 scripts/export_openapi.py
```

Or, with the API running:

```bash
curl -s http://localhost:8008/openapi.json | python3 -m json.tool > docs/api/openapi.json
```

## Configuration

| Env var | Default | Effect |
|---------|---------|--------|
| `DATABASE_URL` | from root `.env` | SQLAlchemy connection string. |
| `SKIP_DB_VERIFY` | unset | When `1`, the app boots without verifying the DB (used by `export_openapi.py`). |
| `ADVISE_DS_MODELS` | `AdVise/api/ds_models` | Directory the API reads joblib artifacts from. In Compose, `./AdVise/ds/models` is mounted read-only to this path. |
| `ADVISE_PREFECT_AVAILABLE` | `true` (in Compose) | Toggles the `prefect_available` field on `/v1/status`. |
| `ADVISE_SKIP_PREFECT_CREATIVE` | unset | When `1`, the preview endpoint bypasses Prefect and calls `creative_extract` directly. |
| `ADVISE_LEGACY_MODEL_ONLY_FOR` | unset | Limits which target metrics fall back to the legacy `model.pkl`. |

## Related

- [App](app.md) — the only consumer of `/v1/*` in production.
- [Data Science](ds-models.md) — the joblib bundles the API loads and what each predicts.
- [Database ERD](erd.md) — the schema behind the SQLAlchemy models.
- [Orchestration](orchestration.md) — the Prefect creative-extraction flow that wraps part of `POST /v1/predictions/preview`.
