# Root `scripts/`

Small utilities and Prefect flows that live **outside** the Docker service images but support the repo. Everything here runs from the **repository root** (the parent of `scripts/`), which is also the working directory for `docker compose`.

## File overview

| File | Kind | Purpose |
|------|------|---------|
| [`export_openapi.py`](#export_openapipy) | Plain CLI | Dump FastAPI OpenAPI schema to `docs/api/openapi.json`. |
| [`prefect.yaml`](#prefectyaml-deployment-manifest) | Manifest | Declares Prefect deployments for the three flows below. |
| [`docker_compose_manager.py`](#docker_compose_managerpy) | Prefect flow | `compose_flow` — up / down / restart the Docker Compose stack. |
| [`safe_compose_up.py`](#safe_compose_uppy) | Prefect flow | `safe_compose_up_flow` — retry `compose up -d --build` with cleanup and full stdout/stderr capture. |
| [`auto_db_update.py`](#auto_db_updatepy) | Prefect flow | `auto_db_update_flow` — re-run `etl_db` and then restart the `back` service. |

All three Prefect flows share the same conventions:

- `ROOT = Path(__file__).resolve().parents[1]` — the repo root is the compose `cwd`.
- `find_docker_compose_command()` auto-detects whether to invoke `docker compose` (v2 plugin) or `docker-compose` (legacy v1) and raises if neither is on `PATH`.
- A worker started **outside** the repo root will fail with “no `docker-compose.yml`” — always run `prefect worker start` from the repo root.

---

## `export_openapi.py`

Writes the FastAPI OpenAPI schema to **`docs/api/openapi.json`** without booting Postgres (it sets `SKIP_DB_VERIFY=1` and a placeholder `DATABASE_URL` before importing the app).

```bash
cd /path/to/repo
python3 scripts/export_openapi.py
```

See also [API / OpenAPI refresh](api/README.md) and [Prefect orchestration](api/prefect-orchestration.md) for how this fits with the API-side Prefect flow.

---

## `prefect.yaml` (deployment manifest)

Declares three Prefect 3 deployments, all bound to the **`advise-pool`** work pool:

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

These appear in the Prefect UI **only after** you register them:

```bash
export PREFECT_API_URL="http://127.0.0.1:4200/api"   # adjust to your server
prefect work-pool create advise-pool --type process  # once; skip if it exists
prefect deploy --prefect-file scripts/prefect.yaml --all
prefect worker start --pool advise-pool              # required for runs to execute
```

If the worker reports the pool as **NOT READY**, it usually means no `prefect worker start` is running for `advise-pool`.

---

## `docker_compose_manager.py`

**Flow:** `compose_flow(command, detach=True, build=True, profiles=None, remove_volumes=False)` — registered as deployment **`docker-compose-manager`**.

A thin Prefect wrapper around `docker compose` for the AdVise stack.

### Tasks

| Task | Retries | What it does |
|------|---------|--------------|
| `RunComposeCommand` | 2 (5s delay) | Runs an arbitrary `docker compose <args>` with `cwd=ROOT`. Logs the resolved command. |
| `ComposeUp` | 2 (5s delay) | Builds `up` args (`-d`, `--build`, optional `--profile`) and calls `RunComposeCommand`. |
| `ComposeDown` | 2 (5s delay) | Builds `down` args (`-v` if `remove_volumes`, `--remove-orphans` by default) and calls `RunComposeCommand`. |

### Supported `command` values

- `up` — `ComposeUp` (build + detach by default, optional profiles).
- `down` — `ComposeDown`.
- `restart` — `ComposeDown` then `ComposeUp` (in-flow restart, **not** the lightweight `docker compose restart`).

Any other value raises `ValueError`.

### CLI

The module is also runnable directly and exposes a small argparse CLI for local use:

```bash
# From the repo root
python3 scripts/docker_compose_manager.py up                  # detach + build
python3 scripts/docker_compose_manager.py up --no-build
python3 scripts/docker_compose_manager.py up --profile dev
python3 scripts/docker_compose_manager.py down --volumes      # drop volumes
python3 scripts/docker_compose_manager.py restart
python3 scripts/docker_compose_manager.py start               # up, then wait for Ctrl+C, then down
```

The `start` command is interactive — `wait_for_stop_signal()` blocks until **SIGINT** (or **SIGTERM**, where available), then runs `down`. Useful for "boot the stack from my terminal and tear it down when I'm done".

### When to use this vs. plain `docker compose`

Reach for `compose_flow` (or the deployment) when you want Prefect-visible run history and retries around routine up/down/restart. Use raw `docker compose` for one-off debugging.

---

## `safe_compose_up.py`

**Flow:** `safe_compose_up_flow(max_retries=3, delay_seconds=5)` — registered as deployment **`docker-compose-recovery`**.

The "harder" variant of bringing the stack up: it loops at the **flow** level (not the task level) and runs a cleanup step between attempts.

### Tasks

| Task | What it does |
|------|--------------|
| `run_compose` | Runs `docker compose <args>` with `capture_output=True` so **stdout and stderr are logged** when the command fails. Validates that `docker-compose.yml` exists at `ROOT` first; raises `FileNotFoundError` with a clear hint if not. |
| `cleanup` | `docker compose down --remove-orphans` — runs after every failed attempt to leave the host in a clean state before the next retry. |

### Behaviour

For each attempt `1..max_retries`:

1. Log `Attempt i/max_retries`.
2. Try `docker compose up -d --build`.
3. On success, return.
4. On failure, log the captured **stdout/stderr**, run `cleanup()`, sleep `delay_seconds`, and try again.

If all attempts fail, the flow raises `RuntimeError("All retries failed")`.

### When to use this vs. `compose_flow up`

Use **`docker-compose-recovery`** when bring-up is flaky (e.g. a slow image pull, an `etl_db` race, a port that briefly stays bound after a previous run) and you'd rather have the orchestrator clean up and retry than fail fast. Use **`docker-compose-manager`** for normal day-to-day up/down/restart.

### Direct invocation

```bash
python3 scripts/safe_compose_up.py        # default: 3 retries, 5s delay
```

---

## `auto_db_update.py`

**Flow:** `auto_db_update_flow()` — registered as deployment **`auto-db-update`**.

Refresh the database from CSVs and bounce the API so it picks up any schema/model changes.

### Tasks

| Task | Retries | What it does |
|------|---------|--------------|
| `run_compose` | 2 (5s delay) | Generic `docker compose <args>` runner used by the two tasks below. |
| `run_etl` | inherits | `docker compose up etl_db` — runs the one-shot ETL container that rebuilds tables from `data_raw/`. See [ETL](etl.md). |
| `restart_api` | inherits | `docker compose restart back` — graceful restart of the FastAPI service. |

The flow runs them **sequentially**: ETL must finish before the API restart. On failure it logs the exception and re-raises so the run shows as **Failed** in the Prefect UI.

### When to use this

- After dropping new CSVs into `data_raw/` and wanting them reflected in Postgres.
- After changing SQLAlchemy models or ETL code and wanting a clean rebuild + a fresh API process.

### Direct invocation

```bash
python3 scripts/auto_db_update.py
```

---

## Troubleshooting compose flows

If `docker compose up` (or the recovery flow) exits **non-zero**, open the failing **task log** in the Prefect UI. With `safe_compose_up.py` you'll see the full Docker output inline; with `docker_compose_manager.py` you'll see the resolved command and you may need to re-run with stderr visible locally to see Docker's own error.

Common causes:

- **`.env` missing or wrong at the repo root.** Compose needs `DB_*` and friends — same failure as a manual `docker compose up --build`.
- **`etl_db` exits non-zero.** Missing `data_raw/` CSVs or a preprocessing error stops the stack before `back` starts.
- **Ports already in use** (`5432`, `8008`, `8501`, …) — a stale container or another local process is bound.
- **Docker Desktop not running**, or `docker compose` not on `PATH` (the script falls back to `docker-compose` but raises `RuntimeError("Docker Compose not found")` if neither is available).
- **Wrong `cwd`.** The worker process must run from the **repo root** (parent of `scripts/`); otherwise the flow either can't find `docker-compose.yml` (`safe_compose_up.py` raises a clear error) or compose itself errors with "no configuration file provided".

See [ETL](etl.md) for the `etl_db` pipeline and [Prefect orchestration](api/prefect-orchestration.md) for how these flows relate to the API-side creative extraction flow.

---

## Adding scripts

Keep scripts **idempotent** where possible (safe to re-run). For new Prefect flows:

1. Drop a `*.py` next to the existing ones, exposing one `@flow`-decorated function.
2. Add an entry to `scripts/prefect.yaml` with a unique `name`, the `entrypoint`, and `work_pool.name: advise-pool`.
3. Re-register with `prefect deploy --prefect-file scripts/prefect.yaml --all`.
4. Document it here and link from [Project structure](project-structure.md) if it becomes part of the standard workflow.
