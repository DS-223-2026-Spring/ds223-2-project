"""
Optional inference from DS-trained joblib models (tier classifiers).

Mount trained artifacts into the API container, e.g. Compose:
  ./AdVise/ds/models:/api/ds_models:ro
Set ADVISE_DS_MODELS=/api/ds_models (default when that path exists).
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, Optional, Tuple

log = logging.getLogger(__name__)

_DEFAULT_REL = os.path.join(os.path.dirname(__file__), "ds_models")


def models_dir() -> str:
    return os.environ.get("ADVISE_DS_MODELS", _DEFAULT_REL)


def _has_artifact(target_metric: str) -> bool:
    base = models_dir()
    return os.path.isfile(os.path.join(base, f"model_{target_metric}.pkl"))


def predict_tier_if_available(
    target_metric: str, feature_row: Dict[str, Any]
) -> Optional[Tuple[str, float, str]]:
    """
    If model + encoders exist for `target_metric`, run sklearn predict + proba max.
    Returns (tier_label, confidence_0_1, model_version) or None if skipped.
    """
    if not _has_artifact(target_metric):
        return None
    try:
        import joblib as jl  # noqa: WPS433
        from sklearn.ensemble import RandomForestClassifier  # noqa: F401
    except ImportError:
        log.warning("joblib/sklearn not installed; skipping DS inference")
        return None

    root = models_dir()
    try:
        model = jl.load(os.path.join(root, f"model_{target_metric}.pkl"))
        encoders = jl.load(os.path.join(root, f"encoders_{target_metric}.pkl"))
    except Exception as exc:  # noqa: BLE001
        log.warning("Failed to load DS artifacts for %s: %s", target_metric, exc)
        return None

    import pandas as pd  # noqa: WPS433

    cols_path = os.path.join(root, f"feature_cols_{target_metric}.pkl")
    if not os.path.isfile(cols_path):
        return None
    feature_cols: list = jl.load(cols_path)
    missing = [c for c in feature_cols if c not in feature_row]
    if missing:
        log.debug("DS inference skipped; missing features: %s", missing)
        return None

    df = pd.DataFrame([{c: feature_row[c] for c in feature_cols}])
    for col, le in encoders.items():
        if col not in df.columns:
            continue
        known = set(le.classes_)
        df[col] = (
            df[col]
            .astype(str)
            .apply(lambda x, k=known, d=le: x if x in k else d.classes_[0])
        )
        df[col] = le.transform(df[col])

    X = df[feature_cols]
    tier = model.predict(X)[0]
    confidence = float(max(model.predict_proba(X)[0]))
    return str(tier), confidence, target_metric
