# API folder

This folder hosts the **machine-readable OpenAPI schema** for the FastAPI service.

- **`openapi.json`** — exported snapshot of the live `/openapi.json`. Used by tooling and external consumers; not rendered by MkDocs.

The human-readable API documentation lives on the top-level [API](../api.md) page.

## Refresh `openapi.json`

Offline (no DB required — sets `SKIP_DB_VERIFY=1`):

```bash
cd /path/to/repo
python3 scripts/export_openapi.py
```

Or from a running API:

```bash
curl -s http://localhost:8008/openapi.json | python3 -m json.tool > docs/api/openapi.json
```

See [API § Refreshing openapi.json](../api.md#refreshing-openapijson) and [Orchestration § scripts/export_openapi.py](../orchestration.md#6-misc-utility-scriptsexport_openapipy).
