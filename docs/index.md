# Welcome to Demo Project

This demo project shows how to use Docker and Docker Compose to connect multiple services: PostgreSQL, a FastAPI backend, a Streamlit app, and pgAdmin.

## Documentation pages

- [API (FastAPI entry and routes)](api.md) — `main` and related modules
- [API models (SQLAlchemy)](api_models.md) — database model definitions
- [Streamlit application](app.md) — `app` package reference
- [ETL and orchestration](etl.md) — design notes and next steps
- [Group demo script](demo.md) — talking points and demo flow

The file **`index.html`** in this same folder is a static HTML page you can open directly in a browser (it is not used as the MkDocs home page, because the site is generated from this `index.md` file; MkDocs will skip copying `index.html` into `site/` when `index.md` is present, which is expected).

## How it works?

[End-to-end tutorial (slides)](https://hovhannisyan91.github.io/DS223_Group_Project/#/title-slide).

## Services

* **Database** – PostgreSQL.
* **API** – FastAPI that talks to PostgreSQL.
* **App** – Streamlit UI that calls the API.
* **pgAdmin** – Web UI to inspect and manage the database.
* **Docs** – This site, built with [MkDocs](https://www.mkdocs.org/) (run `mkdocs serve` from the repository root to preview).

