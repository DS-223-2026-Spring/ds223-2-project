# Endpoint spec alignment (PDF / stakeholders vs repo)

Historical assignee sheets described **multipart** `POST /v1/predictions/preview` (campaign fields + uploaded files), **Prefect-triggered extraction** waited inside the same HTTP request, Streamlit routes under **`pages/2_Campaign_Input.py`** and **`pages/3_Prediction_Results.py`**, and durable **`run_id`** storage.

**Current implementation (this repo):**

| Topic | Implemented | Notes |
|-------|--------------|-------|
| `GET /v1/meta/enums`, `GET /v1/status` | Yes | See [v1-endpoints.md](v1-endpoints.md). |
| `POST /v1/predictions/preview` | JSON body only | `PredictionPreviewRequest`. No multipart; creative features are stubs server-side. |
| Prefect integration in API path | No | Creative pipeline lives under `AdVise/ds/Feature_extraction_automatation_pipelines.py`; trigger via CLI / deployment worker, not from FastAPI. |
| `GET /v1/prediction-runs/{run_id}` | Yes | Ephemeral dict in process memory; lost on restart. |
| Saved campaigns CRUD | Partial | Demo routes under `/campaigns` (in-memory JSON); Postgres-backed lists under **`/v1/campaigns/`** (read-only SELECT). |

**Frontend locations:** Streamlit entry is **`AdVise/app/app.py`**; multi-page flows live under **`AdVise/app/pages/`** when present (`2_Campaign_Input.py` uses **`AdVise/app/api_client.py`**).

**Recommendation for external PDF/versioned specs:** Replace or annotate any row that mandates “payload + files + Prefect in one request” with either:

1. **As-built:** JSON-only preview ([v1-endpoints.md](v1-endpoints.md)), or  
2. **Target architecture:** Separate upload endpoint + preview by `creative_id`/`run_id`, async job + polling (explicitly labelled “future”).
