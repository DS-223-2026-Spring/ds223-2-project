# Orchestration

AdVise uses **Prefect 3** to make every non-trivial side-effect — bringing the stack up, refreshing the database, scoring a new creative, batch-saving features — a tracked, retried, replayable flow.

There are **four Prefect flows** in the repo, split across two layers:

| Layer | Module | Flow | Triggered by | Purpose |
|-------|--------|------|--------------|---------|
| API | `AdVise/api/creative_prefect.py` | `api-creative-extraction-preview` | `POST /v1/predictions/preview` (when an image is sent) | Run image-based creative feature extraction inside the HTTP request, with retries. |
| DS batch | `AdVise/ds/Feature_extraction_automatation_pipelines.py` | `process_new_creative_flow` | Operator / scheduler | Extract creative features for ads rows that don't have them yet and `UPDATE ads`. |
| Compose ops | `scripts/docker_compose_manager.py` | `compose_flow` | Deployment `docker-compose-manager` | Wrap `docker compose` up / down / restart for the AdVise stack. |
| Compose ops | `scripts/safe_compose_up.py` | `safe_compose_up_flow` | Deployment `docker-compose-recovery` | Retry `docker compose up -d --build` with cleanup and full stdout/stderr capture. |
| Data refresh | `scripts/auto_db_update.py` | `auto_db_update_flow` | Deployment `auto-db-update` | Run the `etl_db` container and bounce the `back` service. |

The repo also ships a one-shot **ETL container** (`etl_db`) that isn't a Prefect flow itself but is the workload the `auto-db-update` flow drives.

---

## 1. API preview flow (FastAPI)

When **`POST /v1/predictions/preview`** receives **`creative_image_base64`**, `AdVise/api/creative_prefect.py` decodes the image to a temp file and runs the Prefect flow **`api-creative-extraction-preview`** (task **`APICreativeExtract`**, retries 2 × 5 s). The underlying logic is the same as `creative_extract.extract_creative_features`; Prefect adds retries and gives the failure a traceable run ID.

To bypass Prefect for debugging (direct Python call, no retries):

```bash
export ADVISE_SKIP_PREFECT_CREATIVE=1
```

on the `back` service. The status endpoint exposes whether the wrapper is on:

```json
GET /v1/status → { ..., "prefect_available": true }
```

In the default Compose stack `ADVISE_PREFECT_AVAILABLE=true` is set on `back` so `prefect_available` is `true`. The field is **UX-only**; toggling it does not change behaviour, it only tells the frontend what to expect.

See [API § Creative features](api.md#creative-features).

---

## 2. DS batch pipeline (PostgreSQL writes)

`AdVise/ds/Feature_extraction_automatation_pipelines.py` runs the same `extract_creative_features` logic over many `ads` rows, with one extra task that writes the results back to Postgres.

| Task | Retries | What it does |
|------|---------|--------------|
| `Extract Image Features` | 2 (5 s delay) | Wraps `extract_creative_features`. |
| `Save Features to DB` | 3 (10 s delay) | `UPDATE ads` via `db_helpers.get_connection`; transient Postgres errors get retried. |

Step ordering is **sequential** inside the flow: extract must finish before save; no parallelism today.

**Running it locally** (Postgres reachable; see root `.env`):

```bash
cd AdVise/ds
DB_HOST=127.0.0.1 python3 Feature_extraction_automatation_pipelines.py
```

**As a Prefect deployment / `serve`:** uncomment the `process_new_creative_flow.serve(...)` block at the bottom of the DS flow module and supply `parameters=` for flow arguments (`image_path`, `campaign_id`). `serve()` blocks until interrupted.

See [Data Science § Creative feature extraction](ds-models.md#creative-feature-extraction-image-based).

---

## 3. Repo-level flows under `scripts/`

Three flow modules plus a deployment manifest. They all share three conventions:

- `ROOT = Path(__file__).resolve().parents[1]` — the **repo root** is the compose `cwd`.
- `find_docker_compose_command()` auto-detects `docker compose` (v2 plugin) vs `docker-compose` (legacy v1) and raises if neither is on `PATH`.
- A worker started **outside** the repo root will fail with "no `docker-compose.yml`" — always start `prefect worker` from the repo root.

### `prefect.yaml` (deployment manifest)

Binds the three flows below to a single work pool (`advise-pool`):

```1:17:scripts/prefect.yaml
name: advise-prefect

deployments:
  - name: docker-compose-manager
    entrypoint: scripts/docker_compose_manager.py:compose_flow
    work_pool:
      name: advise-pool

  - name: docker-compose-recovery
    entrypoint: scripts/safe_compose_up.py:safe_compose_up_flow
    work_pool:
      name: advise-pool

  - name: auto-db-update
    entrypoint: scripts/auto_db_update.py:auto_db_update_flow
    work_pool:
      name: advise-pool
```

### `docker_compose_manager.py` — routine up/down/restart

**Flow:** `compose_flow(command, detach=True, build=True, profiles=None, remove_volumes=False)` → deployment **`docker-compose-manager`**.

A thin Prefect wrapper around `docker compose` for the AdVise stack.

| Task | Retries | What it does |
|------|---------|--------------|
| `RunComposeCommand` | 2 (5 s) | Runs `docker compose <args>` with `cwd=ROOT`. Logs the resolved command. |
| `ComposeUp` | 2 (5 s) | Builds `up` args (`-d`, `--build`, optional `--profile`) and calls `RunComposeCommand`. |
| `ComposeDown` | 2 (5 s) | Builds `down` args (`-v` if `remove_volumes`, `--remove-orphans` by default) and calls `RunComposeCommand`. |

Supported `command` values: `up`, `down`, `restart` (= down → up). Anything else raises `ValueError`.

It also exposes a small CLI for local use:

```bash
python3 scripts/docker_compose_manager.py up                  # detach + build
python3 scripts/docker_compose_manager.py up --no-build
python3 scripts/docker_compose_manager.py up --profile dev
python3 scripts/docker_compose_manager.py down --volumes      # drop volumes
python3 scripts/docker_compose_manager.py restart
python3 scripts/docker_compose_manager.py start               # up, then wait for Ctrl+C, then down
```

The `start` command is interactive — `wait_for_stop_signal()` blocks on SIGINT/SIGTERM, then runs `down`.

### `safe_compose_up.py` — flaky bring-up with retries

**Flow:** `safe_compose_up_flow(max_retries=3, delay_seconds=5)` → deployment **`docker-compose-recovery`**.

The "harder" variant of bringing the stack up. It loops at the **flow** level and runs a cleanup step between attempts.

| Task | What it does |
|------|--------------|
| `run_compose` | Runs `docker compose <args>` with `capture_output=True` so **stdout and stderr are logged** when the command fails. Validates `docker-compose.yml` exists at `ROOT` first; raises `FileNotFoundError` with a clear hint otherwise. |
| `cleanup` | `docker compose down --remove-orphans` — runs after every failed attempt to leave the host in a clean state before retrying. |

For each attempt `1..max_retries`:

1. Try `docker compose up -d --build`.
2. On success, return.
3. On failure, log captured stdout/stderr, run `cleanup()`, sleep `delay_seconds`, retry.

If all attempts fail, the flow raises `RuntimeError("All retries failed")`.

Direct run:

```bash
python3 scripts/safe_compose_up.py        # default: 3 retries, 5s delay
```

### `auto_db_update.py` — ETL refresh + API restart

**Flow:** `auto_db_update_flow()` → deployment **`auto-db-update`**.

Refresh the database from CSVs and bounce the API so it picks up any schema/model changes.

| Task | Retries | What it does |
|------|---------|--------------|
| `run_compose` | 2 (5 s) | Generic `docker compose <args>` runner used by the two below. |
| `run_etl` | inherits | `docker compose up etl_db` — the one-shot ETL container; see § ETL below. |
| `restart_api` | inherits | `docker compose restart back` — graceful restart of the FastAPI service. |

The flow runs them **sequentially**: ETL must finish before the API restart. On failure it logs the exception and re-raises so the run shows as **Failed** in the Prefect UI.

Direct run:

```bash
python3 scripts/auto_db_update.py
```

### When to pick which flow

- **Routine** stack up / down / restart → **`docker-compose-manager`** (`compose_flow`).
- **Flaky** bring-up where you want automatic cleanup + retry → **`docker-compose-recovery`** (`safe_compose_up_flow`).
- **Data refresh** (rebuild Postgres from `data_raw/` and bounce the API) → **`auto-db-update`** (`auto_db_update_flow`).

---

## 4. Registering deployments and starting a worker

In Prefect 3, deployments only appear in the UI **after** you register them, and a deployment is only `READY` while a **worker** is polling its work pool.

```bash
# 1. Start the long-running server (separate terminal — blocks)
prefect server start

# 2. Point the CLI at it
export PREFECT_API_URL="http://127.0.0.1:4200/api"

# 3. Create the work pool once (process-type worker = local subprocess)
prefect work-pool create advise-pool --type process

# 4. Register every deployment in scripts/prefect.yaml
prefect deploy --prefect-file scripts/prefect.yaml --all

# 5. Start a worker — from the repo root (it's compose's cwd)
cd /path/to/repo
prefect worker start --pool advise-pool
```

After step 5 the pool flips to `READY` and the three deployments inherit it.

### Triggering a run

```bash
prefect deployment run "Docker Compose Manager/docker-compose-manager" --param command=up
prefect deployment run "Safe Docker Compose Up with Recovery/docker-compose-recovery"
prefect deployment run "Automatic Database Update Flow/auto-db-update"
```

The worker picks the run off the queue, executes the flow in a subprocess (cwd = where you started the worker → compose finds `docker-compose.yml`), and the run appears in the UI at <http://127.0.0.1:4200>.

### Troubleshooting compose flows

If `docker compose up` fails inside a flow, open the failing task log:

- **`safe_compose_up.py`** captures and logs Docker's **stdout / stderr** inline.
- **`docker_compose_manager.py`** logs the resolved command; re-run locally if you need to see Docker's own stderr.

Common causes:

- **`.env` missing or wrong at the repo root.** Compose needs `DB_*` etc. — same failure as a manual `docker compose up --build`.
- **`etl_db` exits non-zero.** Missing `data_raw/` CSVs or a preprocessing error stops the stack before `back` starts.
- **Ports already in use** (`5432`, `8008`, `8501`, `5050`).
- **Docker Desktop not running.**
- **Wrong worker `cwd`** — must be the **repo root** (parent of `scripts/`).
- **`PREFECT_API_URL` unset** — the CLI defaults to an ephemeral in-process API and never reaches your server.

A common transient failure during `docker compose up --build` is Debian apt mirrors timing out while building `etl_db` (`E: Failed to fetch ... Connection truncated`). It's not a bug in the Dockerfile — it's network flakiness. Retrying (or using `docker-compose-recovery`) is the right move.

---

## 5. ETL pipeline (`etl_db`)

Not a Prefect flow itself, but the workload the `auto-db-update` flow runs and the one-shot loader Compose runs at startup.

### Layout — `AdVise/etl/db/`

```
AdVise/etl/db/
├── Dockerfile
├── docker-entrypoint.sh
├── data_raw/                              # tech_advertising_campaigns_dataset.csv, marketing_campaign_dataset.csv
├── data_clean/                            # training_dataset.csv (from preprocessing; gitignored)
├── sql/
│   ├── schema.sql                         # all CREATE TABLE + indexes + campaign CHECKs
│   ├── db_checks.sql                      # optional sanity queries
│   ├── campaigns_schema_migration.sql     # one-time upgrade old shape → current
│   └── apply_marketing_schema.sh          # local: create DB + apply schema.sql only
└── scripts/
    ├── utils/
    │   ├── db_utils.py
    │   └── db_helpers.py
    ├── preprocessing.py                   # data_raw/*.csv → data_clean/training_dataset.csv
    ├── load_to_db.py                      # TRUNCATE + bulk-insert training_dataset
    └── populate_app_tables.py             # synthetic campaigns/ads/audience/predictions
```

### What `etl_db` does (the one-shot container)

`docker-entrypoint.sh` runs four steps in order; **all must succeed** or the container exits non-zero (and `back` won't start because of `depends_on: condition: service_completed_successfully`):

1. **Apply schema** — `psql … -f sql/schema.sql` creates tables, indexes, CHECK constraints.
2. **Preprocess** — `python scripts/preprocessing.py` reads `data_raw/*.csv` and writes `data_clean/training_dataset.csv`.
3. **Load training table** — `python scripts/load_to_db.py` `TRUNCATE`s `training_dataset` and bulk-inserts from the cleaned CSV. **Idempotent.**
4. **Populate app tables** — `python scripts/populate_app_tables.py` inserts synthetic rows into `campaigns`, `ads`, `audience`, and three `predictions` rows per campaign (one each for `ctr`, `conversion_rate`, `reach_score`, matching the `uq_campaign_metric` UNIQUE constraint).

### Running it manually

```bash
# Compose (the standard path; requires `db` to be running)
docker compose run --rm --build etl_db

# Or step-by-step locally (Postgres reachable):
bash AdVise/etl/db/sql/apply_marketing_schema.sh
python AdVise/etl/db/scripts/preprocessing.py
python AdVise/etl/db/scripts/load_to_db.py
python AdVise/etl/db/scripts/populate_app_tables.py
```

### Required input files

`data_raw/` must contain:

- `tech_advertising_campaigns_dataset.csv`
- `marketing_campaign_dataset.csv`

If either is missing, preprocessing fails, `etl_db` exits non-zero, and `back` / `front` will not start.

### Env

The repo root `.env` is loaded when you `import db_utils`. An optional `AdVise/etl/.env` overrides it; see `AdVise/etl/.env.example`.

---

## 6. Misc utility — `scripts/export_openapi.py`

Not a flow — listed here because it lives next to the orchestration scripts. Writes the FastAPI OpenAPI schema to `docs/api/openapi.json` with `SKIP_DB_VERIFY=1`, so it works offline:

```bash
python3 scripts/export_openapi.py
```

See [API § Refreshing openapi.json](api.md#refreshing-openapijson).

---

## Related

- [API](api.md) — `/v1/status` reports `prefect_available`; `POST /v1/predictions/preview` is the trigger for the API-side flow.
- [Data Science](ds-models.md) — the DS batch flow updates the same `ads` table whose creative features the API reads at inference time.
- [Database ERD](erd.md) — `auto-db-update` rebuilds the live tables shown there.
