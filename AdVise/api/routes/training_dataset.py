from fastapi import APIRouter
from schema import TrainingDatasetCreate, TrainingDatasetResponse

router = APIRouter(prefix="/training-dataset", tags=["Training Dataset"])

training_dataset = {
    1: {
        "platform": "Instagram",
        "budget": 1000.0,
        "duration_days": 30,
        "ctr": 0.10,
        "conversion_rate": 0.03
    }
}

@router.get("/", response_model=dict[int, TrainingDatasetResponse])
def get_training_dataset():
    return {
        row_id: {"id": row_id, **row}
        for row_id, row in training_dataset.items()
    }

@router.post("/", response_model=TrainingDatasetResponse)
def create_training_dataset(row: TrainingDatasetCreate):
    new_id = max(training_dataset.keys()) + 1 if training_dataset else 1
    training_dataset[new_id] = row.model_dump()
    return {"id": new_id, **training_dataset[new_id]}