"""
PostgreSQL helpers for the marketing ETL (same server and database as the FastAPI app).

Uses **`DB_NAME`** from the root `.env` (must match the database in `DATABASE_URL`). If you still
have legacy `MARKETING_DB_NAME` set, it is used as a fallback. Optional **`MARKETING_DATABASE_URL`**
(plain `postgresql://...`) overrides host/user/password/db for psycopg2.

Env loading:
1. Repository **root** `.env` (next to `docker-compose.yml`)
2. Optional **`AdVise/etl/.env`**

Required: `DB_USER`, `DB_PASSWORD` (or `POSTGRES_PASSWORD`). Optional: `DB_NAME` (default `marketing_db`), `POSTGRES_HOST`, `POSTGRES_PORT`, or `MARKETING_DATABASE_URL` (overrides all).
"""
import os
from pathlib import Path
from typing import Any, List, Optional, Sequence, Tuple

import psycopg2
from dotenv import load_dotenv
from psycopg2.extensions import connection as PgConnection


def _load_env_files() -> None:
    """Load `.env` from repo root, then optional `AdVise/etl/.env` (overrides)."""
    here = Path(__file__).resolve()
    # Repo root: directory that contains docker-compose.yml
    path = here.parent
    root: Optional[Path] = None
    for _ in range(14):
        if (path / "docker-compose.yml").is_file():
            root = path
            break
        if path.parent == path:
            break
        path = path.parent
    if root is not None and (root / ".env").is_file():
        load_dotenv(root / ".env", override=False)
    # ETL folder = parents[3] from utils: utils->scripts->db->etl
    etl_dir = here.parents[3]
    if (etl_dir / ".env").is_file():
        load_dotenv(etl_dir / ".env", override=True)


_load_env_files()


def get_connection() -> PgConnection:
    dsn = os.environ.get("MARKETING_DATABASE_URL")
    if dsn:
        return psycopg2.connect(dsn)
    user = os.environ.get("DB_USER", os.environ.get("POSTGRES_USER", "postgres"))
    password = os.environ.get("DB_PASSWORD") or os.environ.get("POSTGRES_PASSWORD")
    if not password:
        raise RuntimeError(
            "Set DB_PASSWORD (or POSTGRES_PASSWORD) in your environment or .env for database access."
        )
    dbname = (
        os.environ.get("DB_NAME")
        or os.environ.get("MARKETING_DB_NAME")
        or "marketing_db"
    )
    return psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=os.environ.get("POSTGRES_HOST", "localhost"),
        port=os.environ.get("POSTGRES_PORT", "5432"),
    )


# -------------------------
# SELECT (READ)
# -------------------------
def fetch_all(query: str) -> List[Tuple[Any, ...]]:
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(query)
        return list(cur.fetchall())
    finally:
        cur.close()
        conn.close()


# -------------------------
# INSERT
# -------------------------
def execute_insert(query: str, values: Sequence[Any]) -> None:
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(query, values)
        conn.commit()
    finally:
        cur.close()
        conn.close()


# -------------------------
# UPDATE / DELETE
# -------------------------
def execute_query(query: str, values: Optional[Sequence[Any]] = None) -> None:
    conn = get_connection()
    cur = conn.cursor()
    try:
        if values is not None:
            cur.execute(query, values)
        else:
            cur.execute(query)
        conn.commit()
    finally:
        cur.close()
        conn.close()
