from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import get_db

router = APIRouter(prefix="/v1/audience", tags=["audience"])


@router.get("/")
def get_audience(db: Session = Depends(get_db)):
    query = text("""
        SELECT *
        FROM audience
        LIMIT 100
    """)

    rows = db.execute(query).mappings().all()

    return {
        "count": len(rows),
        "audience": [dict(row) for row in rows]
    }