from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from schema import AudienceListResponse, AudienceDBResponse
from database import get_db

router = APIRouter(prefix="/v1/audience", tags=["audience"])


@router.get("/", response_model=AudienceListResponse)
def get_audience(db: Session = Depends(get_db)):
    """
    Return audience records from the PostgreSQL audience table.
    """
    query = text("""
        SELECT *
        FROM audience
        LIMIT 100
    """)

    rows = db.execute(query).mappings().all()

    return AudienceListResponse(
        count=len(rows),
        audience=[AudienceDBResponse(**dict(row)) for row in rows]
)