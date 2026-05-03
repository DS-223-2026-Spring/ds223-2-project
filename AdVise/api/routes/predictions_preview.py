"""
Preview predictions aligned with ``campaign_intent`` → CTR / conversion / reach.

Optional DS tier models: mount joblib artifacts (see ``prediction_models.py``).
"""

import os
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

router = APIRouter(prefix="/v1", tags=["predictions"])

prediction_runs = {}

MODEL_VERSION = os.environ.get("MODEL_VERSION", "v1-intent-mapping")


def _placeholder_tier() -> tuple[str, float]:
    return "medium", 0.55


def _input_summary(payload: PredictionPreviewRequest) -> dict:
    if hasattr(payload, "dict"):
        return payload.dict()
    return payload.model_dump()


def _response_to_dict(resp: PredictionPreviewResponse) -> dict:
    if hasattr(resp, "dict"):
        return resp.dict()
    return resp.model_dump()


def _parse_stored_prediction(data: dict) -> PredictionPreviewResponse:
    if hasattr(PredictionPreviewResponse, "model_validate"):
        return PredictionPreviewResponse.model_validate(data)
    return PredictionPreviewResponse.parse_obj(data)


@router.post("/predictions/preview", response_model=PredictionPreviewResponse)
def preview_prediction(payload: PredictionPreviewRequest):
    run_id = str(uuid4())
    intent = payload.campaign_intent.strip()
    target_metric, target_label = resolve_target_metric(intent)

    feature_row = {
        "platform": payload.platform,
        "duration_days": payload.duration_days,
        "campaign_intent": intent,
        "product_type": payload.product_type,
        "cta_type": payload.cta_type,
        "age": "25-34",
        "gender": "unknown",
        "location": "US",
        "interests": "tech",
        "audience_temperature": payload.audience_temperature,
        "customer_type": payload.customer_type,
        "career": "professional",
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
            f"Placeholder tier for `{target_metric}` (`{intent}`). "
            "Mount `./AdVise/ds/models` → `/api/ds_models` and install sklearn/joblib "
            "for live tier inference."
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
        campaign_intent=intent,
        target_metric=target_metric,
        target_label=target_label,
        predicted_tier=predicted_tier,
        prediction_confidence=prediction_confidence,
        recommendations=recs,
        input_summary=_input_summary(payload),
    )

    prediction_runs[run_id] = _response_to_dict(response)
    return response


@router.get("/prediction-runs/{run_id}", response_model=PredictionRunResponse)
def get_prediction_run(run_id: str):
    if run_id not in prediction_runs:
        return PredictionPreviewResponse(
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
        )

    return _parse_stored_prediction(prediction_runs[run_id])
