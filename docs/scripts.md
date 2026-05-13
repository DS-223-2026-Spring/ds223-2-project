# Root `scripts/`

Small utilities that live **outside** the Docker service images but support the repo.

## `export_openapi.py`

Writes the FastAPI OpenAPI schema to **`docs/api/openapi.json`** (no DB connection if **`SKIP_DB_VERIFY=1`** is set by the script).

```bash
cd /path/to/repo
python3 scripts/export_openapi.py
```

See also [API / OpenAPI refresh](api/README.md).

## Adding scripts

Keep scripts **idempotent** where possible (safe to re-run). Prefer documenting new scripts here and linking from [Project structure](project-structure.md) if they are part of the standard workflow.
