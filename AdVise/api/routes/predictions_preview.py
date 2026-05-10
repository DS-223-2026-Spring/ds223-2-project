"""
Preview predictions aligned with ``campaign_intent`` → CTR / conversion / reach.

Loads tier classifiers when joblib artifacts are mounted under ``ADVISE_DS_MODELS``.
Optional base64-encoded creative image runs a **Prefect** flow (``api-creative-extraction-preview``)
that wraps ``creative_extract.extract_creative_features``.
"""

from __future__ import annotations

import base64
import logging
import os
import tempfile
from uuid import uuid4

from fastapi import APIRouter

from campaign_intent import resolve_target_metric
from prediction_models import predict_tier_if_available
from schema import (
    PredictionPreviewRequest,
    PredictionPreviewResponse,
    PredictionRunResponse,
    RecommendationBlock,
)
from creative_prefect import extract_creative_for_preview
from training_vocab import (
    canonical_audience_temperature,
    canonical_campaign_intent,
    canonical_cta_type,
    canonical_customer_type,
    canonical_platform,
    canonical_product_type,
)

try:
    import creative_extract  # noqa: F401 — module must exist when preview sends image
except ImportError:
    creative_extract = None  # type: ignore[misc, assignment]

log = logging.getLogger(__name__)

router = APIRouter(prefix="/v1", tags=["predictions"])

prediction_runs = {}

FEATURE_SNAPSHOT_KEYS = (
    "platform",
    "duration_days",
    "campaign_intent",
    "product_type",
    "cta_type",
    "age",
    "gender",
    "location",
    "interests",
    "audience_temperature",
    "customer_type",
    "career",
    "creative_type",
    "copy_text_length",
    "aspect_ratio",
    "visual_complexity",
    "has_person",
)


def _feature_snapshot(feature_row: dict) -> dict:
    return {k: feature_row[k] for k in FEATURE_SNAPSHOT_KEYS if k in feature_row}

MODEL_VERSION = os.environ.get("MODEL_VERSION", "v1-intent-mapping")


def _placeholder_tier() -> tuple[str, float]:
    return "medium", 0.55


def _input_summary(payload: PredictionPreviewRequest) -> dict:
    if hasattr(payload, "model_dump"):
        return payload.model_dump()
    return payload.dict()


def _response_to_dict(resp: PredictionPreviewResponse) -> dict:
    if hasattr(resp, "model_dump"):
        return resp.model_dump()
    return resp.dict()


def _parse_stored_prediction(data: dict) -> PredictionPreviewResponse:
    if hasattr(PredictionPreviewResponse, "model_validate"):
        return PredictionPreviewResponse.model_validate(data)
    return PredictionPreviewResponse.parse_obj(data)


def _apply_creative_image_base64(
    feature_row: dict,
    b64: str | None,
) -> dict | None:
    """Runs Prefect-wrapped extraction; merges into ``feature_row``; returns feats or None."""
    if not b64 or creative_extract is None:
        return None
    try:
        raw = base64.b64decode(b64.split(",")[-1].strip())
    except Exception as exc:  # noqa: BLE001
        log.warning("creative_image_base64 decode failed: %s", exc)
        return None
    path: str | None = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tf:
            tf.write(raw)
            path = tf.name
        feats = extract_creative_for_preview(path)
        feature_row["creative_type"] = feats.get(
            "creative_type", feature_row["creative_type"]
        )
        feature_row["aspect_ratio"] = feats.get(
            "aspect_ratio", feature_row["aspect_ratio"]
        )
        feature_row["visual_complexity"] = float(
            feats.get("visual_complexity", feature_row["visual_complexity"])
        )
        feature_row["has_person"] = bool(
            feats.get("has_person", feature_row["has_person"])
        )
        return dict(feats)
    except Exception as exc:  # noqa: BLE001
        log.warning("creative feature extraction failed: %s", exc)
        return None
    finally:
        if path:
            try:
                os.unlink(path)
            except OSError:
                pass


@router.post("/predictions/preview", response_model=PredictionPreviewResponse)
def preview_prediction(payload: PredictionPreviewRequest):
    run_id = str(uuid4())
    intent_raw = payload.campaign_intent.strip()
    target_metric, target_label = resolve_target_metric(intent_raw)
    intent_model = canonical_campaign_intent(intent_raw)

    feature_row: dict = {
        "platform": canonical_platform(payload.platform),
        "duration_days": payload.duration_days,
        "campaign_intent": intent_model,
        "product_type": canonical_product_type(payload.product_type),
        "cta_type": canonical_cta_type(payload.cta_type),
        "age": payload.audience_age or "25-34",
        "gender": (payload.audience_gender or "unknown").lower(),
        "location": payload.audience_location or "US",
        "interests": payload.audience_interests or "tech",
        "audience_temperature": canonical_audience_temperature(
            payload.audience_temperature
        ),
        "customer_type": canonical_customer_type(payload.customer_type),
        "career": (payload.career or "professional").lower().replace(" ", "_"),
        "creative_type": "image",
        "copy_text_length": 15,
        "aspect_ratio": "1:1",
        "visual_complexity": 0.5,
        "has_person": False,
        "conversion_rate": 0.07,
        "engagement_score": 5.5,
        "reach_score": 55.0,
        "lead_rate": 0.06,
    }

    creative_feats = _apply_creative_image_base64(
        feature_row, payload.creative_image_base64
    )
    model_feature_snapshot = _feature_snapshot(feature_row)

    inferred = predict_tier_if_available(target_metric, feature_row)
    if inferred:
        tier, confidence, mv_label = inferred
        model_version = f"ds-{mv_label}"
        predicted_tier = tier
        prediction_confidence = confidence
        score = confidence
        hint = (
            f"Model tier `{tier}` for `{target_metric}` "
            f"(confidence {confidence:.2f}). Validate on holdout before launch."
        )
    else:
        model_version = MODEL_VERSION
        predicted_tier, prediction_confidence = _placeholder_tier()
        score = prediction_confidence
        hint = (
            f"Placeholder tier for `{target_metric}` (`{intent_raw}`). "
            "Add joblib artifacts under `./AdVise/ds/models` (see `train.py`) and "
            "install sklearn/joblib in the API image for live tier inference."
        )

    recs = [
        RecommendationBlock(
            rank=1,
            primary_kpi=target_metric,
            score=float(score),
            hint=hint,
        )
    ]
    cc = payload.creative_count or 1
    for idx in range(2, min(cc, 3) + 1):
        recs.append(
            RecommendationBlock(
                rank=idx,
                primary_kpi=target_metric,
                score=max(0.1, float(score) - 0.05 * (idx - 1)),
                hint=(
                    f"Alternative creative #{idx}: compare `{target_metric}` "
                    "to rank 1 when creatives differ."
                ),
            )
        )

    response = PredictionPreviewResponse(
        run_id=run_id,
        status="success",
        model_version=model_version,
        campaign_intent=intent_raw,
        target_metric=target_metric,
        target_label=target_label,
        predicted_tier=predicted_tier,
        prediction_confidence=prediction_confidence,
        recommendations=recs,
        input_summary=_input_summary(payload),
        creative_features=creative_feats,
        model_feature_snapshot=model_feature_snapshot,
    )

    prediction_runs[run_id] = _response_to_dict(response)
    return response


@router.get("/prediction-runs/{run_id}", response_model=PredictionRunResponse)
def get_prediction_run(run_id: str):
    if run_id not in prediction_runs:
        return PredictionRunResponse(
            run_id=run_id,
            status="failed",
            model_version=MODEL_VERSION,
            campaign_intent="",
            target_metric="ctr",
            target_label="",
            predicted_tier=None,
            prediction_confidence=None,
            recommendations=[],
            input_summary={},
            creative_features=None,
            model_feature_snapshot=None,
        )

    return _parse_stored_prediction(prediction_runs[run_id])
