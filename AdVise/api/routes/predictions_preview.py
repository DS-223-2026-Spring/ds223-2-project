from uuid import uuid4

from fastapi import APIRouter
from schema import (
    PredictionPreviewRequest,
    PredictionPreviewResponse,
    PredictionRunResponse,
)

router = APIRouter(prefix="/v1", tags=["predictions"])

prediction_runs = {}


@router.post("/predictions/preview", response_model=PredictionPreviewResponse)
def preview_prediction(payload: PredictionPreviewRequest):
    """
    Validate campaign input and return placeholder prediction recommendations.
    """
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
                "hint": "Strong audience fit. Consider testing this creative first.",
            },
            {
                "rank": 2,
                "primary_kpi": "ctr",
                "score": 0.74,
                "hint": "Good click potential. Improve CTA clarity.",
            },
        ],
        "input_summary": payload.dict(),
    }

    prediction_runs[run_id] = result
    return result


@router.get("/prediction-runs/{run_id}", response_model=PredictionRunResponse)
def get_prediction_run(run_id: str):
    """
    Return the status and stored result for a prediction run.
    """
    if run_id not in prediction_runs:
        return {
            "run_id": run_id,
            "status": "failed",
            "model_version": "v1-placeholder",
            "recommendations": [],
            "input_summary": {},
        }

    return prediction_runs[run_id]