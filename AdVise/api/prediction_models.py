"""
Optional inference from DS-trained joblib models (tier classifiers).

Mount trained artifacts into the API container, e.g. Compose:
  ./AdVise/ds/models:/api/ds_models:ro
Set ADVISE_DS_MODELS=/api/ds_models (default when that path exists).

Reads either per-target tuples (train.py):

  ``model_ctr.pkl``, ``encoders_ctr.pkl``, ``feature_cols_ctr.pkl``

or a legacy single trio:

  ``model.pkl``, ``encoders.pkl``, ``feature_cols.pkl`` (used only if
  ``target_metric`` matches ``ADVISE_LEGACY_MODEL_ONLY_FOR``, default ``ctr``).
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, List, Optional, Tuple

log = logging.getLogger(__name__)

_DEFAULT_REL = os.path.join(os.path.dirname(__file__), "ds_models")


def models_dir() -> str:
    return os.environ.get("ADVISE_DS_MODELS", _DEFAULT_REL)


def _pick_model_bundle(target_metric: str) -> Tuple[str, str, str] | None:
    """
    Prefer ``model_<target>.pkl`` + matching encoders + feature_cols; fall back
    to legacy ``model.pkl``, ``encoders.pkl``, ``feature_cols.pkl``.
    """
    root = models_dir()

    triple = (
        os.path.join(root, f"model_{target_metric}.pkl"),
        os.path.join(root, f"encoders_{target_metric}.pkl"),
        os.path.join(root, f"feature_cols_{target_metric}.pkl"),
    )
    if all(os.path.isfile(p) for p in triple):
        return triple

    legacy = (
        os.path.join(root, "model.pkl"),
        os.path.join(root, "encoders.pkl"),
        os.path.join(root, "feature_cols.pkl"),
    )
    if all(os.path.isfile(p) for p in legacy):
        only_for = os.getenv("ADVISE_LEGACY_MODEL_ONLY_FOR", "ctr").strip().lower()
        if target_metric != only_for:
            log.debug(
                "Legacy trio model.pkl skipped for metric %s (only %s)",
                target_metric,
                only_for,
            )
            return None
        return legacy

    return None


def predict_tier_if_available(
    target_metric: str, feature_row: Dict[str, Any]
) -> Optional[Tuple[str, float, str]]:
    """
    If model + encoders exist for `target_metric`, run sklearn predict + proba max.
    Returns (tier_label, confidence_0_1, model_version) or None if skipped.
    """
    bundle = _pick_model_bundle(target_metric)
    if not bundle:
        return None

    mp, ep, cp = bundle
    try:
        import joblib as jl  # noqa: WPS433
        from sklearn.ensemble import RandomForestClassifier  # noqa: F401
    except ImportError:
        log.warning("joblib/sklearn not installed; skipping DS inference")
        return None

    try:
        model = jl.load(mp)
        encoders = jl.load(ep)
        feature_cols: List[str] = jl.load(cp)
    except Exception as exc:  # noqa: BLE001
        log.warning("Failed to load DS artifacts for %s: %s", target_metric, exc)
        return None

    import pandas as pd  # noqa: WPS433

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
    mv_label = (
        target_metric
        if os.path.basename(mp) == f"model_{target_metric}.pkl"
        else f"{target_metric}-legacy-pkl"
    )
    return str(tier), confidence, mv_label
