from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from schema import AdListResponse, AdDBResponse

from database import get_db

router = APIRouter(prefix="/v1/ads", tags=["ads"])


@router.get("/", response_model=AdListResponse)
def get_ads(db: Session = Depends(get_db)):
    """
    Return ad creative records from the PostgreSQL ads table.
    """
    query = text("""
        SELECT *
        FROM ads
        LIMIT 100
    """)

    rows = db.execute(query).mappings().all()

    return AdListResponse(
        count=len(rows),
        ads=[AdDBResponse(**dict(row)) for row in rows]
    )