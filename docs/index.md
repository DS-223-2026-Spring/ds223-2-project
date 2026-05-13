# AdVise

Dockerized stack: **PostgreSQL**, one-shot **ETL** (`AdVise/etl/db`), **FastAPI** (`AdVise/api`), **Streamlit** (`AdVise/app`), optional **pgAdmin**. Source: **[github.com/DS-223-2026-Spring/ds223-2-project](https://github.com/DS-223-2026-Spring/ds223-2-project)**. Default **`docker compose up --build`** waits for **`etl_db`** to finish before starting **`back`** and **`front`**.

## Documentation map

| Topic | Page |
|-------|------|
| Repo tree, Compose order, env vars | [Project structure](project-structure.md) |
| Database tables + ERD | [Database ERD](erd.md) |
| FastAPI entry + mkdocstrings | [API](api.md) |
| SQLAlchemy models | [API models](api_models.md) |
| **`/v1/*`** JSON examples | [API v1 (examples)](api/v1-endpoints.md) |
| OpenAPI export | [API / OpenAPI refresh](api/README.md) |
| Prefect + creative preview | [Prefect orchestration](api/prefect-orchestration.md) |
| Stakeholder spec notes | [Endpoint spec alignment](api/endpoint-spec-alignment.md) |
| Streamlit pages | [Streamlit app](app.md) |
| ETL steps + `data_raw` | [ETL](etl.md) |
| **`train.py`**, joblib, live inference | [DS models & inference](ds-models.md) |
| Root **`scripts/`** | [Scripts](scripts.md) |
| Demo talking points | [Demo](demo.md) |
| Legacy assumptions tracker | [API assumptions](api_assumptions.md) |

The file **`index.html`** in this folder is a static page you can open directly; MkDocs builds from **`index.md`** and will not treat **`index.html`** as the site home when **`index.md`** exists.

## How it works (slides)

[End-to-end tutorial (slides)](https://hovhannisyan91.github.io/DS223_Group_Project/#/title-slide).

## Services (default Compose)

| Service | Role |
|---------|------|
| **`db`** | PostgreSQL 17; data dir **`./postgres_data`**. |
| **`etl_db`** | One-shot: **`schema.sql`** → preprocessing → **`training_dataset`** → synthetic live tables. |
| **`back`** | FastAPI on **8000** in the network, **8008** on the host; **`/docs`** Swagger. |
| **`front`** | Streamlit on **8501**; calls **`back`** via **`API_URL`**. |
| **`pgadmin`** | Web UI for Postgres (**`PGADMIN_PORT`**, default **5050**). |
| **`ds_batch_visuals`** (profile) | Optional: **`predict.py`** + **`generate_visuals.py`** into **`AdVise/ds/outputs`**. |
| **`ds`** (profile) | Optional Jupyter under **`AdVise/`**. |

Build the doc site from the repo root: **`mkdocs serve`** or **`mkdocs build`** (see **`mkdocs.yaml`**).
