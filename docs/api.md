## API

- [Home](index.md) · [Models (detailed)](api_models.md) · [v1 examples](api/v1-endpoints.md) · [Streamlit app](app.md)

### `main.py`

::: api.main

### `models.py`

::: api.models

### Route groups (summary)

| Prefix | Source | Notes |
|--------|--------|--------|
| **`/v1/campaigns/`**, **`/v1/ads/`**, **`/v1/audience/`**, **`/v1/predictions/`** | `routes/campaigns_v1.py`, `ads_v1.py`, `audience_v1.py`, `predictions_v1.py` | **PostgreSQL** via **`get_db`** — primary product API. |
| **`POST /v1/predictions/preview`**, **`GET /v1/prediction-runs/{run_id}`** | `routes/predictions_preview.py` | Preview + optional DB upsert for **`ads`** / **`predictions`**. |
| **`GET /v1/status`**, **`GET /v1/meta/enums`** | `routes/route2.py`, `routes/meta.py` | Health + enum vocabulary (DB-backed where columns exist). |
| **`/campaigns`**, **`/ads`**, … (no **`v1`**) | `routes/campaigns.py`, etc. | **Legacy in-memory** demos; prefer **`/v1/*`** for real data. |
| **`/training_dataset`**, **`/ext`**, core **`/route2`** | Other routers | Training sample / extensions / misc. |

OpenAPI: **`/openapi.json`**, Swagger UI: **`/docs`**, ReDoc: **`/redoc`**.
