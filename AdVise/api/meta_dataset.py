"""Distinct categorical values from ``training_dataset`` for form dropdowns."""

from __future__ import annotations

from typing import Callable, Mapping

from sqlalchemy import text
from sqlalchemy.orm import Session

WHITE_MAP: Mapping[str, str] = {
    "platform": "platforms",
    "campaign_intent": "campaign_intents",
    "cta_type": "cta_types",
    "audience_temperature": "audience_temperature",
    "customer_type": "customer_types",
    "product_type": "product_types",
    "location": "regions",
    "age": "age_bands",
    "gender": "genders",
    "interests": "interests",
    "career": "careers",
}

_FALLBACK_DEVICES = ["mobile", "desktop", "tablet"]


def _distinct(db: Session, column_sql: str) -> list[str]:
    q = text(
        f"""
        SELECT DISTINCT TRIM("{column_sql}"::text) AS v
        FROM training_dataset
        WHERE "{column_sql}" IS NOT NULL AND TRIM("{column_sql}"::text) != ''
        ORDER BY v
        """
    )
    rows = db.execute(q).fetchall()
    return [str(r[0]) for r in rows if r and r[0] is not None]


def enums_from_training_dataset(db: Session) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for col, resp_key in WHITE_MAP.items():
        try:
            out[resp_key] = _distinct(db, col)
        except Exception:
            out[resp_key] = []
    out["devices"] = list(_FALLBACK_DEVICES)
    return out


def merge_with_fallback(
    primary: Mapping[str, list[str]],
    fallback: Callable[[], dict[str, list[str]]],
) -> dict[str, list[str]]:
    fb = fallback()
    out: dict[str, list[str]] = {}
    for key, fb_vals in fb.items():
        vals = list(primary.get(key, []))
        out[key] = vals if vals else list(fb_vals)
    return out
