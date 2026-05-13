"""
Preview predictions aligned with ``campaign_intent`` → CTR / conversion / reach.

Loads tier classifiers when joblib artifacts are mounted under ``ADVISE_DS_MODELS``.
Optional base64-encoded creative image runs a **Prefect** flow (``api-creative-extraction-preview``)
that wraps ``creative_extract.extract_creative_features``.

When ``campaign_id`` and ``ad_id`` are sent (e.g. after ``POST /v1/campaigns/``), the matching
``ads`` row is updated with creative fields (including extraction output when an image is sent),
then PostgreSQL ``predictions`` is upserted for ``(campaign_id, predicted_metric)`` (unique per
campaign and target metric; same preview again updates tier/confidence and ``ad_id``).
"""

from __future__ import annotations

import base64
import logging
import os
import tempfile
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from campaign_intent import resolve_target_metric
from creative_prefect import extract_creative_for_preview
from database import get_db
from prediction_models import predict_tier_if_available
from schema import (
    PredictionPreviewRequest,
    PredictionPreviewResponse,
    PredictionRunResponse,
    RecommendationBlock,
)
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


def _persist_ad_and_prediction(
    db: Session,
    *,
    campaign_id: int,
    ad_id: int,
    feature_row: dict,
    cta_type: str,
    creative_url: str | None,
    predicted_metric: str,
    predicted_tier: str,
    confidence: float,
) -> int:
    row = db.execute(
        text("SELECT campaign_id FROM ads WHERE ad_id = :ad_id"),
        {"ad_id": ad_id},
    ).fetchone()
    if not row:
        raise HTTPException(status_code=400, detail="ad_id not found")
    if int(row[0]) != int(campaign_id):
        raise HTTPException(
            status_code=400,
            detail="ad_id does not belong to the given campaign_id",
        )

    upd = db.execute(
        text(
            """
            UPDATE ads SET
                creative_type = :creative_type,
                cta_type = :cta_type,
                copy_text_length = :copy_text_length,
                aspect_ratio = :aspect_ratio,
                visual_complexity = :visual_complexity,
                has_person = :has_person,
                creative_url = COALESCE(:creative_url, creative_url)
            WHERE ad_id = :ad_id AND campaign_id = :campaign_id
            """
        ),
        {
            "creative_type": str(feature_row.get("creative_type", "image")),
            "cta_type": cta_type,
            "copy_text_length": int(feature_row.get("copy_text_length", 15)),
            "aspect_ratio": str(feature_row.get("aspect_ratio", "1:1")),
            "visual_complexity": float(feature_row.get("visual_complexity", 0.5)),
            "has_person": bool(feature_row.get("has_person", False)),
            "creative_url": (
                creative_url.strip()
                if creative_url is not None and creative_url.strip()
                else None
            ),
            "ad_id": ad_id,
            "campaign_id": campaign_id,
        },
    )
    if upd.rowcount == 0:
        raise HTTPException(
            status_code=500,
            detail="UPDATE ads affected 0 rows (ad_id / campaign_id mismatch?)",
        )

    ins = db.execute(
        text(
            """
            INSERT INTO predictions (
                campaign_id, ad_id, predicted_metric, predicted_tier, confidence
            )
            VALUES (
                :campaign_id, :ad_id, :metric, :tier, :confidence
            )
            ON CONFLICT ON CONSTRAINT uq_campaign_metric
            DO UPDATE SET
                ad_id = EXCLUDED.ad_id,
                predicted_tier = EXCLUDED.predicted_tier,
                confidence = EXCLUDED.confidence
            RETURNING prediction_id
            """
        ),
        {
            "campaign_id": campaign_id,
            "ad_id": ad_id,
            "metric": predicted_metric,
            "tier": str(predicted_tier),
            "confidence": float(confidence),
        },
    ).mappings().first()
    if not ins:
        raise HTTPException(status_code=500, detail="prediction INSERT returned no row")
    db.commit()
    return int(ins["prediction_id"])


@router.post("/predictions/preview", response_model=PredictionPreviewResponse)
def preview_prediction(payload: PredictionPreviewRequest, db: Session = Depends(get_db)):
    run_id = str(uuid4())
    intent_raw = payload.campaign_intent.strip()
    target_metric, target_label = resolve_target_metric(intent_raw)
    intent_model = canonical_campaign_intent(intent_raw)

    cid = payload.campaign_id
    aid = payload.ad_id
    if (cid is None) ^ (aid is None):
        raise HTTPException(
            status_code=422,
            detail="Provide both campaign_id and ad_id to persist the preview, or omit both.",
        )

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

    prediction_id = None
    if cid is not None and aid is not None:
        try:
            cta_for_ad = str(feature_row["cta_type"])
            asset_url = (payload.creative_asset_url or "").strip() or None
            prediction_id = _persist_ad_and_prediction(
                db,
                campaign_id=cid,
                ad_id=aid,
                feature_row=feature_row,
                cta_type=cta_for_ad,
                creative_url=asset_url,
                predicted_metric=target_metric,
                predicted_tier=str(predicted_tier),
                confidence=float(prediction_confidence),
            )
        except HTTPException:
            db.rollback()
            raise
        except Exception as exc:  # noqa: BLE001
            db.rollback()
            log.exception("Failed to persist preview (ads / predictions): %s", exc)
            raise HTTPException(
                status_code=500,
                detail=f"Could not save ads/prediction rows: {exc}",
            ) from exc

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
        prediction_id=prediction_id,
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
            prediction_id=None,
        )

    return _parse_stored_prediction(prediction_runs[run_id])
