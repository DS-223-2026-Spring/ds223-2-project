"""
Campaign intent → prediction target (aligned with DS train.py / predict.py).

The live ``predictions`` table stores at most one row per ``(campaign_id, predicted_metric)``
(unique constraint ``uq_campaign_metric``); ``ad_id`` points at the creative last scored for
that outcome. Marketing UX resolves one primary outcome per intent. Classification models
(when present under ``AdVise/ds/models/``) are trained per target column name below.
"""

from __future__ import annotations

from typing import Dict, Optional, Tuple

# Normalized keys (lowercase) → SQL / model artifact column name
INTENT_TO_TARGET_METRIC: Dict[str, str] = {
    "awareness": "reach_score",
    "sales": "conversion_rate",
    "leads": "conversion_rate",
    "traffic": "ctr",
    "engagement": "ctr",
    "conversion": "conversion_rate",
    "lead_generation": "conversion_rate",
}

TARGET_LABELS: Dict[str, str] = {
    "ctr": "Predicted CTR tier (traffic / engagement objective)",
    "conversion_rate": "Predicted conversion rate tier (sales / leads)",
    "reach_score": "Predicted reach tier (awareness)",
}


def normalize_intent(campaign_intent: str) -> str:
    return (campaign_intent or "").strip().lower()


def resolve_target_metric(campaign_intent: str) -> Tuple[str, str]:
    """
    Returns (metric_key, human_label).
    Unknown intents default to CTR to match safest generic behaviour.
    """
    key = normalize_intent(campaign_intent)
    metric = INTENT_TO_TARGET_METRIC.get(key, "ctr")
    return metric, TARGET_LABELS.get(metric, TARGET_LABELS["ctr"])
