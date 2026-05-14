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

## Route groups (overview)

| Prefix | Source | Notes |
|--------|--------|-------|
| **`/v1/campaigns/`**, **`/v1/ads/`**, **`/v1/audience/`**, **`/v1/predictions/`** | `routes/campaigns_v1.py`, `ads_v1.py`, `audience_v1.py`, `predictions_v1.py` | PostgreSQL via `get_db`. **Primary product API.** |
| **`POST /v1/predictions/preview`**, **`GET /v1/prediction-runs/{run_id}`** | `routes/predictions_preview.py` | Live preview; optional DB upsert into `ads` / `predictions`. |
| **`GET /v1/status`**, **`GET /v1/meta/enums`** | `routes/route2.py`, `routes/meta.py` | Health + enum vocabulary (DB-backed where columns exist). |
| `/campaigns`, `/ads`, ... (no `v1` prefix) | `routes/campaigns.py`, etc. | **Legacy in-memory** demos — keep around for tutorials; production UI should always call `/v1/*`. |
| `/training-dataset`, `/ext`, core `/status` | `routen.py`, `training_dataset.py`, `route2.py` | Training-data sampling / extensions / liveness. |

OpenAPI: **`/openapi.json`**. Swagger UI: **`/docs`**. ReDoc: **`/redoc`**.

## SQLAlchemy models — `models.py`

Mirror the live tables in `AdVise/etl/db/sql/schema.sql` (see [Database ERD](erd.md)). Used by every `/v1/*` route through `database.get_db`.

::: api.models
    options:
        show_source: true

## Endpoint reference

Base URLs:

| Context | URL |
|---------|-----|
| Docker Compose (host machine) | `http://localhost:8008` |
| Streamlit container → API | `http://back:8000` |

The canonical machine-readable contract is `/openapi.json`. The tables and examples below mirror `AdVise/api/schema.py`.

### Endpoint summary

Every route the FastAPI app exposes, at a glance. **Bold rows are the endpoints used by the Streamlit frontend in production.**

| Method | Path | Source | Functionality |
|--------|------|--------|---------------|
| GET | `/` | `main.py` | Root pointer to docs (`{"product":"AdVise","docs":"/docs","redoc":"/redoc"}`). |
| GET | `/status` | `route2.py` | Cheap liveness probe (no DB). Returns `{"product":"AdVise","component":"api","ok":true}`. |
| **GET** | **`/v1/status`** | **`route2.py`** | **Backend health + upload limits + `prefect_available` flag. Used by the Streamlit connection banner.** |
| **GET** | **`/v1/meta/enums`** | **`meta.py`** | **Dropdown vocabulary, sourced from `DISTINCT training_dataset` columns with static fallbacks.** |
| **POST** | **`/v1/predictions/preview`** | **`predictions_preview.py`** | **Run one tier prediction for the metric matching `campaign_intent`; optionally upsert `ads` + `predictions`.** |
| GET | `/v1/prediction-runs/{run_id}` | `predictions_preview.py` | Replay a preview by `run_id` from the in-process dict. |
| **GET** | **`/v1/campaigns/`** | **`campaigns_v1.py`** | **List up to 100 campaigns from Postgres.** |
| **POST** | **`/v1/campaigns/`** | **`campaigns_v1.py`** | **Insert campaign + audience + placeholder ad in one transaction; returns the new IDs.** |
| GET | `/v1/ads/` | `ads_v1.py` | List up to 100 ads from Postgres. |
| GET | `/v1/audience/` | `audience_v1.py` | List up to 100 audience rows from Postgres. |
| GET | `/v1/predictions/` | `predictions_v1.py` | List up to 100 prediction rows from Postgres. |
| GET / POST / PUT / DELETE | `/campaigns/`, `/campaigns/{id}` | `campaigns.py` | **Legacy** in-memory demo CRUD. Not backed by Postgres. |
| GET / POST | `/ads/` | `ads.py` | Legacy in-memory demo CRUD. |
| GET / POST | `/audience/` | `audience.py` | Legacy in-memory demo CRUD. |
| GET / POST | `/predictions/` | `predictions.py` | Legacy in-memory demo CRUD. |
| GET / POST | `/training-dataset/` | `training_dataset.py` | Tiny tutorial CRUD seeded with one row. |
| GET | `/ext/placeholder` | `routen.py` | Placeholder for additional domain routers. |
| GET | `/docs`, `/redoc`, `/openapi.json` | FastAPI default | Swagger UI / ReDoc / OpenAPI schema. |

The detail sections below walk through the **production `/v1/*`** surface in the order a typical session calls them.

---

### Liveness and health

#### `GET /` — root

Returns links to interactive docs. Useful for a smoke test.

```json
{ "product": "AdVise", "docs": "/docs", "redoc": "/redoc" }
```

#### `GET /status` — cheap liveness

Hits no database. Used by Compose health checks / external load balancers that need a sub-millisecond probe.

```json
{ "product": "AdVise", "component": "api", "ok": true }
```

#### `GET /v1/status`

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

The Streamlit app reads this on every page load — a green **✓ Backend connected** banner means the call returned `200`; anything else flips the UI into degraded mode.

---

### Vocabulary

#### `GET /v1/meta/enums`

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

---

### Predictions

#### `POST /v1/predictions/preview`

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

**Status codes:**

| Code | Meaning |
|------|---------|
| `200` | Prediction returned. `prediction_id` is `null` when neither `campaign_id` nor `ad_id` were sent. |
| `400` | `ad_id` not found, or `ad_id` doesn't belong to `campaign_id`. |
| `422` | Sent only one of `campaign_id` / `ad_id` (must be both or neither). |
| `500` | Internal — couldn't persist `ads` / `predictions`. Body's `detail` describes the failed step. |

##### Single outcome per preview

`campaign_intent` resolves to **exactly one** `target_metric` + `target_label`. The API loads **one** classifier bundle per metric; a preview scores **only** that metric — **not** CTR, conversion, and reach at once. Canonical mapping in `AdVise/api/campaign_intent.py` (`INTENT_TO_TARGET_METRIC`):

| Campaign intent (normalized) | `target_metric` |
|------------------------------|-----------------|
| `awareness` | `reach_score` |
| `traffic`, `engagement` | `ctr` |
| `sales`, `leads`, `conversion`, `lead_generation` | `conversion_rate` |
| unknown / other | `ctr` (default) |

See [Data Science](ds-models.md) for the model behind each metric.

##### Creative features

Pass `creative_image_base64` (first image only). The API decodes a temp file and runs `creative_prefect.extract_creative_for_preview`, which executes the Prefect flow `api-creative-extraction-preview` (with retries). Set `ADVISE_SKIP_PREFECT_CREATIVE=1` on `back` to bypass Prefect for debugging. Without an image, preview falls back to stub creative fields. See [Orchestration](orchestration.md) for the flow details.

Tier scoring uses the joblib models under `AdVise/ds/models` (mounted at `/api/ds_models` on `back`). The legacy `model.pkl` is used only for `ctr` unless `ADVISE_LEGACY_MODEL_ONLY_FOR` is set.

##### Persistence rules

| `campaign_id` | `ad_id` | Result |
|---------------|---------|--------|
| `null` | `null` | Preview-only — no DB write; `prediction_id` is `null` in the response. |
| set | set | **UPDATE** `ads` with the creative fields (and `creative_url` if provided), then **UPSERT** `predictions` on the `uq_campaign_metric` constraint (`campaign_id`, `predicted_metric`). Repeat previews of the same metric overwrite tier / confidence / `ad_id`. |
| only one of the two | | `422 Unprocessable Entity`. |

The persistence path runs `_persist_ad_and_prediction`, which first verifies the `ad_id` exists and belongs to `campaign_id` before any write — mismatches are rejected with `400`.

#### `GET /v1/prediction-runs/{run_id}`

Replay a preview by the `run_id` issued in `POST /v1/predictions/preview`. Storage is **in-memory** on the API process (`prediction_runs` dict); restarting the container clears it. Always returns `200`:

- When found: same shape as the preview response.
- When missing: a `PredictionRunResponse` with `status: "failed"`, `predicted_tier: null`, `prediction_confidence: null`, and empty `recommendations` / `input_summary`. The error is conveyed in the body, not the status code.

---

### Campaigns, ads, audience, predictions (PostgreSQL)

The primary product CRUD. All four routers use `database.get_db` (SQLAlchemy session) and the SQL is raw `text(...)` for transparency. List endpoints are capped at **100 rows**.

#### `GET /v1/campaigns/`

Returns a count + list of `campaigns` rows. Example:

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

#### `POST /v1/campaigns/`

Persists a campaign in **one transaction**: insert into `campaigns`, then `audience`, then a **placeholder `ads` row** (with `creative_type='image'`, `aspect_ratio='1:1'`, `copy_text_length=15`, `visual_complexity=0.5`, `has_person=false`, empty URL). The placeholder ad gives the preview endpoint an `ad_id` to update later. Any failure rolls back all three inserts.

**Request body** (`CampaignCreateRequest`) — campaign + audience fields aligned with the `audience` table and the preview API:

```json
{
  "campaign_name": "Spring push",
  "campaign_intent": "awareness",
  "platform": "instagram",
  "budget": 500,
  "duration_days": 7,
  "product_type": "software",
  "cta_type": "learn_more",
  "audience_age": "25-34",
  "audience_gender": "female",
  "audience_location": "US",
  "audience_interests": "tech",
  "audience_temperature": "cold",
  "customer_type": "new",
  "career": "professional"
}
```

**Response `200`** (`CampaignCreateResponse`) — the new IDs plus the campaign columns returned from SQL `RETURNING`:

```json
{
  "campaign_id": 17,
  "audience_id": 17,
  "ad_id": 17,
  "campaign_name": "Spring push",
  "campaign_intent": "awareness",
  "platform": "instagram",
  "budget": 500.0,
  "duration_days": 7,
  "product_type": "software",
  "cta_type": "learn_more"
}
```

**Status codes:** `200` on success, `400` for any database error (constraint violation, type mismatch — `detail` carries the SQL message), `500` for the rare case where the `RETURNING` clause yields no row.

The Streamlit Campaign Input page calls this **before** `POST /v1/predictions/preview` so that the prediction has a real `ad_id` / `campaign_id` to persist against.

#### `GET /v1/ads/`

Returns up to 100 rows from `ads` (`AdListResponse` = `{count, ads: [...]}`). Each row is the full `ads` schema: `ad_id`, `campaign_id`, `creative_type`, `cta_type`, `copy_text_length`, `aspect_ratio`, `visual_complexity`, `has_person`, `creative_url`, `created_at`. Read-only — `ads` rows are created by `POST /v1/campaigns/` (placeholder) and **updated** by `POST /v1/predictions/preview` when `campaign_id` + `ad_id` are supplied.

#### `GET /v1/audience/`

Returns up to 100 rows from `audience` (`AudienceListResponse` = `{count, audience: [...]}`). Each row: `audience_id`, `campaign_id`, `age`, `gender`, `location`, `interests`, `audience_temperature`, `customer_type`, `career`, `created_at`. Read-only — `audience` rows are written by `POST /v1/campaigns/`.

#### `GET /v1/predictions/`

Returns up to 100 rows from `predictions` (`PredictionListResponse` = `{count, predictions: [...]}`). Each row: `prediction_id`, `campaign_id`, `ad_id`, `predicted_metric`, `predicted_tier`, `confidence`, `created_at`. Note the **`uq_campaign_metric` UNIQUE constraint** on `(campaign_id, predicted_metric)` — at most one row per campaign per target metric. Updates flow exclusively through `POST /v1/predictions/preview`.

---

### Legacy in-memory demos (do not use in production)

The non-`v1` routers (`campaigns.py`, `ads.py`, `audience.py`, `predictions.py`, `training_dataset.py`) predate the Postgres-backed `/v1/*` API. They store data in module-level Python dicts that are lost on restart and **don't share state with Postgres**. Keep them around because the tutorial slides reference them; production UI should always call `/v1/*`.

| Method + path | Behaviour |
|---------------|-----------|
| `GET /campaigns/` | List the in-memory dict (one seeded row). |
| `GET /campaigns/{id}` | `200` with that row or `404` if missing. |
| `POST /campaigns/` | Insert by auto-incrementing the max key in the dict. |
| `PUT /campaigns/{id}` | Replace by id; `404` if missing. |
| `DELETE /campaigns/{id}` | Remove by id; returns the deleted row; `404` if missing. |
| `GET /ads/` | List the in-memory ads dict. |
| `POST /ads/` | Insert into the in-memory ads dict. |
| `GET /audience/` | List the in-memory audience dict. |
| `POST /audience/` | Insert into the in-memory audience dict. |
| `GET /predictions/` | List the in-memory predictions dict. |
| `POST /predictions/` | Insert into the in-memory predictions dict. |
| `GET /training-dataset/` | List one tutorial row. |
| `POST /training-dataset/` | Append to the tutorial dict. |
| `GET /ext/placeholder` | Stub for future domain routes — returns `{"message": "..."}`. |

These all use the lightweight Pydantic models from `schema.py` (`CampaignCreate`, `AdCreate`, …) — **not** the `*DBResponse` models the `/v1/*` routes use, so the request/response shapes differ from the Postgres variants on purpose.

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
