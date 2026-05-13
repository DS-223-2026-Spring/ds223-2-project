from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from schema import PredictionDBResponse, PredictionListResponse
from database import get_db

router = APIRouter(prefix="/v1/predictions", tags=["predictions"])


@router.get("/", response_model=PredictionListResponse)
def get_predictions(db: Session = Depends(get_db)):
    """
    Return prediction records from the PostgreSQL predictions table.
    """
    query = text("""
        SELECT *
        FROM predictions
        LIMIT 100
    """)

    rows = db.execute(query).mappings().all()

    return PredictionListResponse(
        count=len(rows),
        predictions=[PredictionDBResponse(**dict(row)) for row in rows]
    )