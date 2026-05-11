from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import get_db

router = APIRouter(prefix="/v1/predictions", tags=["predictions"])


@router.get("/")
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

    return {
        "count": len(rows),
        "predictions": [dict(row) for row in rows]
    }