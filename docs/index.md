# AdVise

**AdVise** is an AI-powered marketing-analytics platform that predicts the potential success of an advertising campaign **before** it goes live. The user supplies campaign goal, audience, budget, and creative; AdVise returns a tier prediction (`low` / `medium` / `high`) on the metric that matches the campaign's intent — `CTR`, `conversion_rate`, or `reach_score`.

The stack is a five-service Dockerized application, each component is documented on its own page:

| Component | What it is | Page |
|-----------|------------|------|
| **App** | Streamlit frontend — the campaign form, preview, and result charts the user sees. | [App](app.md) |
| **API** | FastAPI backend — `/v1` REST endpoints, Swagger docs, model serving. | [API](api.md) |
| **Data Science** | Training pipeline (`train.py`), the three tier classifiers (`model_ctr`, `model_conversion_rate`, `model_reach_score`) and live inference. | [Data Science](ds-models.md) |
| **Database** | PostgreSQL: live tables `campaigns` / `ads` / `audience` / `predictions` plus offline `training_dataset`. | [Database ERD](erd.md) |
| **Orchestration** | Prefect — API-side creative-feature extraction, DS batch flow, and Docker/ETL automation under `scripts/`. | [Orchestration](orchestration.md) |

## Quick start

From the repository root:

```bash
docker compose up --build
```

Compose waits for `etl_db` to finish (one-shot loader) before it starts `back` (API) and `front` (UI). Defaults:

| Service | Port (host) | Purpose |
|---------|-------------|---------|
| `db` | `5432` | PostgreSQL 17 (data dir `./postgres_data`). |
| `etl_db` | — | One-shot: `schema.sql` → preprocessing → `training_dataset` → synthetic live rows. |
| `back` | `8008` | FastAPI; Swagger UI at <http://localhost:8008/docs>. |
| `front` | `8501` | Streamlit UI at <http://localhost:8501>. |
| `pgadmin` | `5050` | Optional Postgres web UI. |

## The campaign-intent → metric mapping

A single preview returns **one** tier prediction. Which metric is chosen depends on the campaign's intent (canonical mapping in `AdVise/api/campaign_intent.py`):

| Campaign intent | Target metric |
|-----------------|---------------|
| `awareness` | `reach_score` |
| `traffic`, `engagement` | `ctr` |
| `sales`, `leads`, `conversion`, `lead_generation` | `conversion_rate` |
| unknown / other | `ctr` (default) |

This is the contract that the **API**, the **Data Science** models, and the **App** all agree on. See each component's page for details.

## Team

| Name | Role |
|------|------|
| Natali Minasyan | Project / Product Manager |
| Milena Sargsyan | Data Scientist |
| Hayk Gevorgyan | Backend Developer (FastAPI) |
| Emilya Sepoyan | Database Developer (PostgreSQL) |
| Rita Chamiyan | Frontend Developer (Streamlit) |
| Nare Kechechyan | Orchestration (Prefect) |

Source: <https://github.com/DS-223-2026-Spring/ds223-2-project>
