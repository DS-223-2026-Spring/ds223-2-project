#!/usr/bin/env python3
"""Write FastAPI OpenAPI schema to docs/api/openapi.json (offline; no DB connect)."""

import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "api" / "openapi.json"

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:unused@localhost:5432/marketing_db",
)
os.environ.setdefault("SKIP_DB_VERIFY", "1")

import sys

sys.path.insert(0, str(ROOT / "AdVise" / "api"))

from main import app  # noqa: E402


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(app.openapi(), indent=2))
    print(f"Wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
