# ETL and orchestration

- [Home](index.md) · [API models](api_models.md) · [Schema diagram](imgs/star_schema.png)

## `AdVise/etl/` layout

| Path | Role |
|------|------|
| **`AdVise/etl/db/`** | Marketing pipeline, SQL schema, **`Dockerfile`**, and **`docker-entrypoint.sh`**. Compose service **`etl_db`** (one-shot) runs this pipeline before the **API** starts. |

### `AdVise/etl/db/` (marketing)

```
AdVise/etl/db/
  data_raw/          # place source CSVs for preprocessing
  data_clean/        # final_dataset.csv (from preprocessing; gitignored)
  sql/
    schema.sql
    db_checks.sql
    apply_marketing_schema.sh
  scripts/
    utils/
      db_utils.py
    preprocessing.py
    load_to_db.py
    load_metrics.py
```

**Suggested order (local, Postgres running):**

1. `CREATE DATABASE` + schema: `bash AdVise/etl/db/sql/apply_marketing_schema.sh` (with `DB_USER`, `DB_PASSWORD`, `DB_NAME` (default `marketing_db`), `POSTGRES_HOST` from root `.env`).
2. `python AdVise/etl/db/scripts/preprocessing.py` (inputs in `data_raw/`).
3. `python AdVise/etl/db/scripts/load_to_db.py` (truncates `campaign_metrics`, `interactions`, `users`, and `ads`, then reloads from `data_clean/final_dataset.csv` so runs are idempotent).
4. `python AdVise/etl/db/scripts/load_metrics.py` — `interaction_id` = row index + 1; must match interaction order.

`db_checks.sql` (use the same `DB_NAME` as in `.env`, default `marketing_db`): `psql -d marketing_db -f AdVise/etl/db/sql/db_checks.sql`

**Env:** the **repo root** `.env` (same as Compose) is loaded automatically when you `import` **`db_utils`**. You do not need a separate `AdVise/etl/.env` unless you want overrides; then copy or symlink: `cp ../../.env AdVise/etl/.env` or `ln -s ../../.env AdVise/etl/.env`. See **`AdVise/etl/.env.example`**.

## Docker Compose (default `up`)

From the repository root, **`docker compose up --build`** starts **`db`**, then runs **`etl_db`** once after `db` is healthy, then starts **`api`** (only if **`etl_db` exits with code 0) and **`app`**.

- **Required:** add **`social_media_ad_optimization.csv`** and **`marketing_campaign_dataset.csv`** under **`AdVise/etl/db/data_raw/`** before `up`. If preprocessing fails, **`etl_db`** fails and **`api` / `app`** will not start.
- **Idempotent ETL:** `load_to_db.py` truncates the four marketing tables and reloads from the CSV, so a second `docker compose up` does not duplicate rows.
- **pgAdmin** may start in parallel with **`etl_db`**; it only needs **`db`**.

To run the ETL image alone: `docker compose run --rm --build etl_db` (same entrypoint; **`db`** must be running).

**Image / Dockerfile:** **`AdVise/etl/db/Dockerfile`**.
