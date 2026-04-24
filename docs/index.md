# AdVise

This project uses Docker and Docker Compose to connect **AdVise** services: PostgreSQL, a one-shot marketing ETL under **`AdVise/etl`**, a FastAPI backend, a Streamlit app, and pgAdmin. The **ETL** runs before the API in the default stack (requires source CSVs in `AdVise/etl/db/data_raw/`). Data science / Jupyter work lives in **`AdVise/ds`**.

## Documentation pages

- [API (FastAPI entry and routes)](api.md) — `main` and related modules
- [API models (SQLAlchemy)](api_models.md) — database model definitions
- [Streamlit application](app.md) — `app` package reference
- [ETL and orchestration](etl.md) — design notes and next steps
- [Group demo script](demo.md) — talking points and demo flow
- [API Assumptions and Pending Dependencies](api_assumptions.md)

The file **`index.html`** in this same folder is a static HTML page you can open directly in a browser (it is not used as the MkDocs home page, because the site is generated from this `index.md` file; MkDocs will skip copying `index.html` into `site/` when `index.md` is present, which is expected).

## How it works?

[End-to-end tutorial (slides)](https://hovhannisyan91.github.io/DS223_Group_Project/#/title-slide).

## Services

* **Database** – PostgreSQL.
* **ETL** – Marketing pipeline under `AdVise/etl/db` (Compose service `etl_db`, runs before `back` when you `docker compose up`).
* **ds** – Jupyter / modeling under `AdVise/ds` (optional Compose `data-science` profile).
* **API** – FastAPI that talks to PostgreSQL.
* **Front** – Streamlit UI that calls the API (Compose service **`front`**; code in **`AdVise/app/`**).
* **pgAdmin** – Web UI to inspect and manage the database.
* **Docs** – This site, built with [MkDocs](https://www.mkdocs.org/) (run `mkdocs serve` from the repository root to preview).

