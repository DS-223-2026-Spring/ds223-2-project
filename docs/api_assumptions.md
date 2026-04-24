# API Assumptions and Pending Dependencies

## Current API Status

The backend currently includes:

- FastAPI project structure
- Swagger/OpenAPI documentation
- Dummy CRUD endpoints for campaigns
- Placeholder request/response schemas (Pydantic)
- Dockerized services (API, DB, pgAdmin, Streamlit)



## API Assumptions

The current implementation assumes:

1. `campaigns` is a core resource of the system.
2. Endpoints are currently using in-memory data (not DB yet).
3. Schemas are placeholders and may change later.
4. Frontend will consume FastAPI endpoints via HTTP.
5. Backend runs inside Docker container (`back` service).

---

## Pending Dependencies

Still need confirmation from PM & DB Developer:

1. Final resource names (campaigns, ads, etc.)
2. Final database schema (tables, columns)
3. Required endpoints for frontend
4. Connecting API to real database
5. Final validation rules
6. Standard error response format

