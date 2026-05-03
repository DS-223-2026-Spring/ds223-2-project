"""
Database configuration for the FastAPI app.

`etl_db` populates the SAME PostgreSQL instance (`db` in docker-compose) via
`AdVise/etl/db/docker-entrypoint.sh` (schema.sql, preprocessing, load_to_db,
populate_app_tables). This service must use a `DATABASE_URL` that points at that
database — e.g. inside Compose:

  postgresql+psycopg2://USER:PASS@db:5432/marketing_db

The API does not connect to ETL code directly; it connects to Postgres after ETL
has run (see `back.depends_on.etl_db`).
"""

import os
from pathlib import Path

import sqlalchemy as sql
import sqlalchemy.ext.declarative as declarative
import sqlalchemy.orm as orm
from dotenv import load_dotenv
from sqlalchemy import text


def _load_env_files() -> None:
    base = Path(__file__).resolve().parent
    for candidate in (base / ".env", base.parent.parent / ".env"):
        if candidate.is_file():
            load_dotenv(candidate)
            return
    load_dotenv()


def get_db():
    """Yield a database session (same DB the ETL pipeline writes to)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_database_connection() -> None:
    """Fail fast at startup if Postgres is unreachable."""
    if os.environ.get("SKIP_DB_VERIFY", "").lower() in ("1", "true", "yes"):
        return
    if not DATABASE_URL:
        raise RuntimeError(
            "DATABASE_URL is not set. For Docker Compose use the same DB as ETL "
            "(host `db`, DB name matching DB_NAME / marketing_db)."
        )
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))


_load_env_files()

DATABASE_URL = os.environ.get("DATABASE_URL")

engine = sql.create_engine(DATABASE_URL)

Base = declarative.declarative_base()

SessionLocal = orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)
