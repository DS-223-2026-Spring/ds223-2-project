# Prefect — orchestration

Prefect is used in two places: **inside the API** for creative feature extraction on preview, and at the **repo root** under `scripts/` for Docker / ETL automation via three flow modules and a deployment manifest (`prefect.yaml`).

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

The repo ships three Prefect flow modules plus a deployment manifest under **`scripts/`**. Full per-file reference (tasks, retries, CLI usage) lives in [Scripts](../scripts.md); this section is the orchestration-level summary.

| File | Flow | Deployment name | Role |
|------|------|-----------------|------|
| **`docker_compose_manager.py`** | `compose_flow` | `docker-compose-manager` | Prefect-wrapped `docker compose` **up / down / restart** (with `ComposeUp` / `ComposeDown` tasks, retries 2 × 5s). Also exposes a local CLI. |
| **`safe_compose_up.py`** | `safe_compose_up_flow` | `docker-compose-recovery` | Retry `docker compose up -d --build` up to `max_retries` times; runs `down --remove-orphans` between attempts and logs full **stdout / stderr** from Docker on failure. |
| **`auto_db_update.py`** | `auto_db_update_flow` | `auto-db-update` | Sequential **ETL refresh + API restart**: `docker compose up etl_db` → `docker compose restart back`. |
| **`prefect.yaml`** | — | — | Declares all three deployments above against work pool `advise-pool`. |
| **`export_openapi.py`** | — | — | Plain utility (not a flow): writes **`docs/api/openapi.json`** from the FastAPI app with `SKIP_DB_VERIFY=1`. |

### Registering deployments (Prefect 3)

Point the CLI at your long-running server, then deploy:

```bash
export PREFECT_API_URL="http://127.0.0.1:4200/api"   # adjust host/port
prefect work-pool create advise-pool --type process  # once; skip if pool exists
prefect deploy --prefect-file scripts/prefect.yaml --all
```

Start a worker so the work pool becomes **ready** and runs can execute (run this from the **repo root** — it's compose's `cwd`):

```bash
prefect worker start --pool advise-pool
```

After this, the Prefect UI lists deployments **`docker-compose-manager`**, **`docker-compose-recovery`**, and **`auto-db-update`**.

### When to pick which flow

- **Routine** stack up / down / restart → **`docker-compose-manager`** (`compose_flow`).
- **Flaky** bring-up where you want automatic cleanup + retry → **`docker-compose-recovery`** (`safe_compose_up_flow`).
- **Data refresh** (rebuild Postgres from `data_raw/` and bounce the API) → **`auto-db-update`** (`auto_db_update_flow`).

### Troubleshooting compose flows

If `docker compose up` fails inside a flow, open the task log:

- **`safe_compose_up.py`** captures and logs Docker's **stdout / stderr** inline (look at the failing `run_compose` task).
- **`docker_compose_manager.py`** logs the resolved command but streams Docker output to the worker's terminal; re-run locally if you need to see stderr.

Common causes: missing root **`.env`**, **`etl_db`** failure (see [ETL](../etl.md)), port conflicts (5432 / 8008 / 8501), Docker not running, or the worker started from the wrong directory (must be the parent of `scripts/`).
