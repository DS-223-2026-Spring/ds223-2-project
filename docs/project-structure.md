# Repository layout

High-level map of this repo (paths relative to the repository root).

## Top level

| Path | Purpose |
|------|---------|
| **`docker-compose.yml`** | **`db`**, **`etl_db`**, **`back`**, **`front`**, **`pgadmin`**; optional profiles **`batch-visuals`**, **`data-science`** (`ds`). |
| **`mkdocs.yaml`** | MkDocs + Material site (`docs/`). |
| **`scripts/`** | Repo tooling (e.g. OpenAPI export). |
| **`docs/`** | MkDocs Markdown sources. |
| **`.env`** | Create locally (not committed): **`DB_*`**, **`PGADMIN_*`**, etc. |

## `AdVise/` — product code

| Path | Purpose |
|------|---------|
| **`AdVise/api/`** | FastAPI app: **`main.py`**, **`database.py`**, **`schema.py`**, **`prediction_models.py`**, **`routes/`** (legacy CRUD + **`/v1/*`** PostgreSQL routes, **`predictions_preview`**). |
| **`AdVise/app/`** | Streamlit UI: **`app.py`**, **`pages/`** (`1_Home`, `2_Campaign_Input`, `3_Prediction_Results`), **`api_client.py`**. |
| **`AdVise/ds/`** | Training / inference: **`train.py`**, **`predict.py`**, **`modeling_related_files.py`**, **`models/*.pkl`** (mounted into **`back`** as **`/api/ds_models`**). |
| **`AdVise/etl/db/`** | ETL image: **`sql/schema.sql`**, **`docker-entrypoint.sh`**, **`scripts/`** (`preprocessing.py`, `load_to_db.py`, `populate_app_tables.py`), **`data_raw/`** (required CSVs). |

## Compose service order (default `up`)

1. **`db`** — PostgreSQL (waits for healthy).
2. **`etl_db`** — one-shot: schema → preprocessing → **`training_dataset`** load → synthetic **`campaigns` / `ads` / `audience` / `predictions`**.
3. **`back`** — FastAPI; starts only if **`etl_db`** exits **0**.
4. **`front`** — Streamlit; depends on **`back`**.

**`pgadmin`** may start in parallel with **`etl_db`**; it only needs **`db`**.

## Environment (API / ETL)

| Variable | Typical use |
|----------|-------------|
| **`DB_USER`**, **`DB_PASSWORD`**, **`DB_NAME`** | Postgres + URL built for **`back`**. |
| **`DATABASE_URL`** | Set automatically on **`back`** from **`DB_*`** in Compose; set manually if running the API outside Compose. |
| **`ADVISE_DS_MODELS`** | Directory of joblib artifacts inside **`back`** (default **`/api/ds_models`**). |
| **`ADVISE_PREFECT_AVAILABLE`** | **`GET /v1/status`** → **`prefect_available`** (UX flag for creative extraction wiring). |
| **`ADVISE_SKIP_PREFECT_CREATIVE`** | Set on **`back`** to bypass Prefect for creative preview (debug). |

## Further reading

- [ETL](etl.md) — pipeline steps and local commands.
- [Database ERD](erd.md) — live vs **`training_dataset`** tables.
- [API v1 examples](api/v1-endpoints.md) — JSON shapes for **`/v1/*`**.
- [Scripts](scripts.md) — root **`scripts/`** utilities.
