#!/usr/bin/env bash
# Create DB (default name marketing_db) and apply schema.sql. Requires: psql, DB_USER, DB_PASSWORD
# From repo root:  set -a && source .env && set +a && bash AdVise/etl/db/sql/apply_marketing_schema.sh
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
: "${DB_USER:=postgres}"
: "${DB_PASSWORD:?Set DB_PASSWORD (e.g. from root .env)}"
: "${DB_NAME:=marketing_db}"
: "${POSTGRES_HOST:=localhost}"
: "${POSTGRES_PORT:=5432}"
export PGPASSWORD="${DB_PASSWORD}"
psql -h "${POSTGRES_HOST}" -p "${POSTGRES_PORT}" -U "${DB_USER}" -d postgres \
  -c "CREATE DATABASE ${DB_NAME}" 2>/dev/null || true
psql -h "${POSTGRES_HOST}" -p "${POSTGRES_PORT}" -U "${DB_USER}" -d "${DB_NAME}" -v ON_ERROR_STOP=1 -f "${HERE}/schema.sql"
echo "OK: ${HERE}/schema.sql applied to ${DB_NAME}"
