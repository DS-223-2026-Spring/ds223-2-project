from fastapi import APIRouter
from schema import PredictionCreate, PredictionResponse

router = APIRouter(prefix="/predictions", tags=["Predictions"])

predictions = {
    1: {
        "campaign_id": 1,
        "predicted_ctr": 0.12,
        "predicted_conversion_rate": 0.04
    }
}

@router.get("/", response_model=dict[int, PredictionResponse])
def get_predictions():
    return {
        prediction_id: {"id": prediction_id, **prediction}
        for prediction_id, prediction in predictions.items()
    }

@router.post("/", response_model=PredictionResponse)
def create_prediction(prediction: PredictionCreate):
    new_id = max(predictions.keys()) + 1 if predictions else 1
    predictions[new_id] = prediction.model_dump()
    return {"id": new_id, **predictions[new_id]}