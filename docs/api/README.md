# API documentation (canonical)

- **[v1-endpoints.md](v1-endpoints.md)** — Structured spec with JSON request/response examples aligned with FastAPI schemas in `AdVise/api/schema.py`.
- **[endpoint-spec-alignment.md](endpoint-spec-alignment.md)** — How this repo aligns with older PDF/stakeholder endpoint sheets (multipart preview, Prefect, file paths).

## Refresh OpenAPI JSON

Requires Python dependencies from `AdVise/api/requirements.txt`:

```bash
cd /path/to/repo
python3 scripts/export_openapi.py
```

Or export from a running API:

```bash
curl -s http://localhost:8008/openapi.json | python3 -m json.tool > docs/api/openapi.json
```

## Prefect orchestration

See **[prefect-orchestration.md](prefect-orchestration.md)** for creative pipeline retries and how it relates to `/v1/status` (`ADVISE_PREFECT_AVAILABLE`).
