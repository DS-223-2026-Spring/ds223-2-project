from typing import Optional
from uuid import uuid4

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/v1", tags=["predictions"])

prediction_runs = {}


class PredictionPreviewRequest(BaseModel):
    platform: str
    campaign_intent: str
    product_type: str
    cta_type: str
    audience_temperature: str
    customer_type: str
    budget: float
    duration_days: int
    creative_count: Optional[int] = 1


@router.post("/predictions/preview")
def preview_prediction(payload: PredictionPreviewRequest):
    run_id = str(uuid4())

    result = {
        "run_id": run_id,
        "status": "success",
        "model_version": "v1-placeholder",
        "recommendations": [
            {
                "rank": 1,
                "primary_kpi": "conversion_rate",
                "score": 0.82,
                "hint": "Strong audience fit. Consider testing this creative first."
            },
            {
                "rank": 2,
                "primary_kpi": "ctr",
                "score": 0.74,
                "hint": "Good click potential. Improve CTA clarity."
            }
        ],
        "input_summary": payload.dict()
    }

    prediction_runs[run_id] = result
    return result


@router.get("/prediction-runs/{run_id}")
def get_prediction_run(run_id: str):
    if run_id not in prediction_runs:
        return {
            "run_id": run_id,
            "status": "failed",
            "message": "Prediction run not found."
        }

    return prediction_runs[run_id]