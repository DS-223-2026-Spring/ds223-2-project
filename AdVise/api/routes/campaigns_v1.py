from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import get_db

router = APIRouter(prefix="/v1/campaigns", tags=["campaigns"])


@router.get("/")
def get_campaigns(db: Session = Depends(get_db)):
    """
    Return campaign records from the PostgreSQL campaigns table.
    """
    query = text("""
        SELECT
            campaign_id,
            company,
            campaign_type,
            platform,
            budget,
            duration_days,
            start_date,
            campaign_intent,
            product_type
        FROM campaigns
        LIMIT 100
    """)

    rows = db.execute(query).mappings().all()

    return {
        "count": len(rows),
        "campaigns": [dict(row) for row in rows]
    }