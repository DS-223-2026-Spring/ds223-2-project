# Prefect — orchestration

Prefect is used in two places: **inside the API** for creative feature extraction on preview, and **optionally at the repo root** for Docker / ETL automation when you add the helper scripts and a deployment manifest.

---

## 1. API preview flow (FastAPI)

When **`POST /v1/predictions/preview`** receives **`creative_image_base64`**, **`AdVise/api/creative_prefect.py`** runs Prefect flow **`api-creative-extraction-preview`**, task **`APICreativeExtract`** — same underlying logic as **`creative_extract.extract_creative_features`** with Prefect retries.

Set **`ADVISE_SKIP_PREFECT_CREATIVE=1`** on **`back`** to bypass Prefect for debugging (direct Python call).

**`GET /v1/status` → `prefect_available`** is **`true`** in the default Compose stack (`ADVISE_PREFECT_AVAILABLE=true`), indicating preview extraction is wired through Prefect.

---

## 2. Repo-level deployments (`scripts/prefect.yaml`)

Orchestration for **Docker / ETL** (not the FastAPI preview) lives under **`scripts/`**. Declared deployments include compose helpers and **`auto-db-update`** (ETL refresh + API restart). They only appear in the Prefect UI after **`prefect deploy --prefect-file scripts/prefect.yaml --all`**. Details: [Scripts](../scripts.md).

---

## 3. DS batch pipeline (PostgreSQL writes)

- Flow module: **`AdVise/ds/Feature_extraction_automatation_pipelines.py`**
- Helpers: **`AdVise/ds/creative_extract.py`**

### Tasks and retries

| Task | Retries | Notes |
|------|---------|--------|
| `Extract Image Features` | 2 (5s delay) | Wraps `extract_creative_features`. |
| `Save Features to DB` | 3 (10s delay) | `UPDATE ads` via `db_helpers.get_connection`; transient Postgres errors get retried. |

Step ordering remains **sequential** inside the flow: extract must finish before save; no parallelism today.

### Running the DS pipeline locally

- From **`AdVise/ds/`** (Postgres reachable; see root README **`.env`**):  
  `DB_HOST=127.0.0.1 python3 Feature_extraction_automatation_pipelines.py`
- **Deployment / `serve`:** uncomment the `process_new_creative_flow.serve(...)` block at the bottom of the DS flow module and supply `parameters=` for flow arguments (`image_path`, `campaign_id`). **`serve()` blocks** until interrupted.

---

## 4. Root `scripts/` and Prefect server deployments

**Current contents of `scripts/`** (see also [Scripts](../scripts.md)):

| File | Role |
|------|------|
| **`export_openapi.py`** | Writes **`docs/api/openapi.json`** from the FastAPI app (offline; sets `SKIP_DB_VERIFY`). |

When your team adds **Prefect deployment** helpers next to it, a typical layout is:

| File | Role |
|------|------|
| **`prefect.yaml`** | Declares deployments (names, `entrypoint: scripts/<module>.py:<flow_fn>`, `work_pool`). |
| **`docker_compose_manager.py`** | Prefect flow wrapping `docker compose` up/down/restart. |
| **`safe_compose_up.py`** | Retry **`docker compose up -d --build`** with cleanup and logging (stdout/stderr on failure). |
| **`auto_db_update.py`** | Flow: run **`etl_db`** then **`docker compose restart back`**. |

### Registering deployments (Prefect 3)

Point the CLI at your long-running server, then deploy:

```bash
export PREFECT_API_URL="http://127.0.0.1:4200/api"   # adjust host/port
prefect work-pool create advise-pool --type process   # once; skip if pool exists
prefect deploy --prefect-file scripts/prefect.yaml --all
```

Start a worker so the work pool becomes **ready** and runs can execute:

```bash
prefect worker start --pool advise-pool
```

Example deployment names (when **`prefect.yaml`** is present): **`docker-compose-manager`**, **`docker-compose-recovery`**, **`auto-db-update`**.

### Troubleshooting compose flows

If **`docker compose up`** fails inside a flow, check the **`run_compose`** task logs for **stdout/stderr** (when using the logging-aware `safe_compose_up` implementation). Common causes: missing root **`.env`**, **`etl_db`** failure (see [ETL](../etl.md)), port conflicts, or Docker not running.
