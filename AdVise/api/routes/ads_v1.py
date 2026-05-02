from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import get_db

router = APIRouter(prefix="/v1/ads", tags=["ads"])


@router.get("/")
def get_ads(db: Session = Depends(get_db)):
    query = text("""
        SELECT *
        FROM ads
        LIMIT 100
    """)

    rows = db.execute(query).mappings().all()

    return {
        "count": len(rows),
        "ads": [dict(row) for row in rows]
    }