# Root `scripts/`

Small utilities that live **outside** the Docker service images but support the repo.

## `export_openapi.py`

Writes the FastAPI OpenAPI schema to **`docs/api/openapi.json`** (no DB connection if **`SKIP_DB_VERIFY=1`** is set by the script).

```bash
cd /path/to/repo
python3 scripts/export_openapi.py
```

See also [API / OpenAPI refresh](api/README.md) and [Prefect orchestration](api/prefect-orchestration.md) § *Root scripts* for how Prefect deployments relate when you add them.

## Prefect (`prefect.yaml`)

**`scripts/prefect.yaml`** declares Prefect **deployments** (registered with `prefect deploy --prefect-file scripts/prefect.yaml --all` when `PREFECT_API_URL` points at your server). Only flows listed there appear in the Prefect UI.

| Deployment | Entrypoint | Purpose |
|------------|------------|---------|
| **`docker-compose-manager`** | `docker_compose_manager.py:compose_flow` | Compose up/down/restart flows. |
| **`docker-compose-recovery`** | `safe_compose_up.py:safe_compose_up_flow` | Retry compose up with cleanup. |
| **`auto-db-update`** | `auto_db_update.py:auto_db_update_flow` | Re-run **`etl_db`** then **`docker compose restart back`**. |

If **`docker compose up`** fails with exit code **1**, open the **task log** for **`run_compose`** — it now prints **stdout/stderr** from Docker. Typical causes:

- **`.env`** missing or wrong at repo root (Compose needs **`DB_*`**, etc.).
- **`etl_db`** exits non-zero (missing **`data_raw/`** CSVs, preprocessing error) so **`back`** never starts — same failure as manual **`docker compose up --build`**.
- **Ports** already in use (**5432**, **8008**, **8501**, …).
- **Docker Desktop** not running.

The worker process must use the **repository root** (parent of **`scripts/`**) as compose **`cwd`**; otherwise you get “no `docker-compose.yml`”.

See [ETL](etl.md) for the **`etl_db`** pipeline.

## Adding scripts

Keep scripts **idempotent** where possible (safe to re-run). Prefer documenting new scripts here and linking from [Project structure](project-structure.md) if they are part of the standard workflow.
