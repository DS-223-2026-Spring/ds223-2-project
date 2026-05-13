# Prefect — creative feature pipelines

## API preview flow (FastAPI)

When **`POST /v1/predictions/preview`** receives **`creative_image_base64`**, **`AdVise/api/creative_prefect.py`** runs Prefect flow **`api-creative-extraction-preview`**, task **`APICreativeExtract`** — same underlying logic as **`creative_extract.extract_creative_features`** with Prefect retries.

Set **`ADVISE_SKIP_PREFECT_CREATIVE=1`** on **`back`** to bypass Prefect for debugging (direct Python call).

**`GET /v1/status` → `prefect_available`** is **`true`** in Compose default stack (`ADVISE_PREFECT_AVAILABLE=true`), indicating preview extraction runs through Prefect wiring.

---

## Repo-level deployments (`scripts/prefect.yaml`)

Orchestration for **Docker / ETL** (not the FastAPI preview) lives under **`scripts/`**. Declared deployments include compose helpers and **`auto-db-update`** (ETL refresh + API restart). They only appear in the Prefect UI after **`prefect deploy --prefect-file scripts/prefect.yaml --all`**. Details: [Scripts](../scripts.md).

---

## DS batch pipeline (PostgreSQL writes)

- Flow module: `AdVise/ds/Feature_extraction_automatation_pipelines.py`
- Helpers: `AdVise/ds/creative_extract.py`

### Tasks and retries

| Task | Retries | Notes |
|------|---------|-------|
| `Extract Image Features` | 2 (5s delay) | Wraps `extract_creative_features`. |
| `Save Features to DB` | 3 (10s delay) | `UPDATE ads` via `db_helpers.get_connection`; transient Postgres errors get retried. |

Step ordering remains **sequential** inside the flow: extract must finish before save; no parallelism today.

---

## Running the DS pipeline

- Local one-shot from `AdVise/ds/` (needs Postgres reachable; see main README `.env`):  
  `DB_HOST=127.0.0.1 python3 Feature_extraction_automatation_pipelines.py`
- **Deployment / `serve`:** uncomment the `process_new_creative_flow.serve(...)` block at the bottom of the DS flow module and supply `parameters=` for flow arguments (`image_path`, `campaign_id`). **`serve()` blocks** until interrupted.
