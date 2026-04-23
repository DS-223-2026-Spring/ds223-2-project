#!/usr/bin/env sh
# Run after Postgres is up. Expects: DB_USER, DB_PASSWORD in env, POSTGRES_HOST=db, inputs in data_raw/
set -e
export POSTGRES_HOST="${POSTGRES_HOST:-db}"
: "${DB_NAME:=marketing_db}"
export PGPASSWORD="${DB_PASSWORD:?DB_PASSWORD is required}"
psql -h "$POSTGRES_HOST" -U "${DB_USER:-postgres}" -d postgres -c "CREATE DATABASE ${DB_NAME}" 2>/dev/null || true
psql -h "$POSTGRES_HOST" -U "${DB_USER:-postgres}" -d "$DB_NAME" -v ON_ERROR_STOP=1 -f /app/sql/schema.sql
python /app/scripts/preprocessing.py
python /app/scripts/load_to_db.py
python /app/scripts/load_metrics.py
echo "etl_db pipeline finished"
