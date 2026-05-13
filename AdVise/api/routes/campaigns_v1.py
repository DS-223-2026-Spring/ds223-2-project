from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from schema import CampaignListResponse, CampaignCreateRequest, CampaignCreateResponse, CampaignDBResponse
from database import get_db

router = APIRouter(prefix="/v1/campaigns", tags=["campaigns"])


@router.get("/", response_model=CampaignListResponse)
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

    return CampaignListResponse(
        count=len(rows),
        campaigns=[CampaignDBResponse(**dict(row)) for row in rows]
    )
    
    
@router.post("/", response_model=CampaignCreateResponse)
def create_campaign(payload: CampaignCreateRequest, db: Session = Depends(get_db)):
    """
    Persist a campaign submitted from the frontend into PostgreSQL.
    """
    query = text("""
        INSERT INTO campaigns (
            company,
            campaign_type,
            platform,
            budget,
            duration_days,
            campaign_intent,
            product_type
        )
        VALUES (
            :company,
            :campaign_type,
            :platform,
            :budget,
            :duration_days,
            :campaign_intent,
            :product_type
        )
        RETURNING
            campaign_id,
            company,
            campaign_type,
            platform,
            budget,
            duration_days,
            campaign_intent,
            product_type
    """)

    result = db.execute(query, payload.dict()).mappings().first()
    db.commit()

    return dict(result)