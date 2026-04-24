# ETL and orchestration

- [Home](index.md) · [API models](api_models.md) · [Schema diagram](imgs/star_schema.png)

## `AdVise/etl/` layout

| Path | Role |
|------|------|
| **`AdVise/etl/db/`** | Pipeline: SQL schema, **`Dockerfile`**, **`docker-entrypoint.sh`**. Compose **`etl_db`** (one-shot) applies schema, runs preprocessing, then loads **`training_dataset`** only. |

### `AdVise/etl/db/`

```
AdVise/etl/db/
  data_raw/          # tech_advertising_campaigns_dataset.csv, marketing_campaign_dataset.csv
  data_clean/        # training_dataset.csv (from preprocessing; gitignored)
  sql/
    schema.sql
    db_checks.sql
    apply_marketing_schema.sh
  scripts/
    utils/
      db_utils.py
    preprocessing.py
    load_to_db.py
```

**Suggested order (local, Postgres running):**

1. `CREATE DATABASE` + schema: `bash AdVise/etl/db/sql/apply_marketing_schema.sh` (with `DB_USER`, `DB_PASSWORD`, `DB_NAME`, `POSTGRES_HOST` from root `.env`).
2. `python AdVise/etl/db/scripts/preprocessing.py` — reads **`data_raw/`** CSVs, writes **`data_clean/training_dataset.csv`**.
3. `python AdVise/etl/db/scripts/load_to_db.py` — `TRUNCATE training_dataset` + bulk insert from that CSV (idempotent for the offline table).

Live ERD tables (`campaigns`, `ads`, `audience`, `predictions`) are **not** filled by this batch job; they are intended for user/API input.

`db_checks.sql`: `psql -d marketing_db -f AdVise/etl/db/sql/db_checks.sql` (use the same `DB_NAME` as in `.env`).

**Env:** the repo root **`.env`** is loaded when you `import` **`db_utils`**. Optional **`AdVise/etl/.env`** overrides; see **`AdVise/etl/.env.example`**.

## Docker Compose (default `up`)

From the repository root, **`docker compose up --build`** starts **`db`**, runs **`etl_db`** once after `db` is healthy, then **`back`** (only if **`etl_db` exits 0) and **`front`**.

- **Required in `data_raw/`:** **`tech_advertising_campaigns_dataset.csv`** and **`marketing_campaign_dataset.csv`**. If preprocessing fails, **`etl_db`** fails and **`back` / `front`** will not start.
- **Idempotent offline load:** `load_to_db.py` truncates **`training_dataset`** and reloads from the generated CSV, so re-running **`up`** does not duplicate training rows.
- **pgAdmin** may start in parallel with **`etl_db`**; it only needs **`db`**.

To run the ETL image alone: `docker compose run --rm --build etl_db` (same entrypoint; **`db`** must be running).

**Image / Dockerfile:** **`AdVise/etl/db/Dockerfile`**.
