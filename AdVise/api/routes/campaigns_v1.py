from fastapi import APIRouter, Depends, HTTPException
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
            campaign_name,
            campaign_intent,
            platform,
            budget,
            duration_days,
            product_type,
            cta_type,
            created_at
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
    Persist a campaign, audience row, and a placeholder ad (for preview / predictions FK) in one transaction.
    """
    insert_campaign = text("""
        INSERT INTO campaigns (
            campaign_name,
            campaign_intent,
            platform,
            budget,
            duration_days,
            product_type,
            cta_type
        )
        VALUES (
            :campaign_name,
            :campaign_intent,
            :platform,
            :budget,
            :duration_days,
            :product_type,
            :cta_type
        )
        RETURNING
            campaign_id,
            campaign_name,
            campaign_intent,
            platform,
            budget,
            duration_days,
            product_type,
            cta_type
    """)

    insert_audience = text("""
        INSERT INTO audience (
            campaign_id,
            age,
            gender,
            location,
            interests,
            audience_temperature,
            customer_type,
            career
        )
        VALUES (
            :campaign_id,
            :age,
            :gender,
            :location,
            :interests,
            :audience_temperature,
            :customer_type,
            :career
        )
        RETURNING audience_id
    """)

    insert_ad = text("""
        INSERT INTO ads (
            campaign_id,
            creative_type,
            cta_type,
            copy_text_length,
            aspect_ratio,
            visual_complexity,
            has_person,
            creative_url
        )
        VALUES (
            :campaign_id,
            'image',
            :cta_type,
            15,
            '1:1',
            0.5,
            false,
            ''
        )
        RETURNING ad_id
    """)

    campaign_params = {
        "campaign_name": payload.campaign_name,
        "campaign_intent": payload.campaign_intent,
        "platform": payload.platform,
        "budget": payload.budget,
        "duration_days": payload.duration_days,
        "product_type": payload.product_type,
        "cta_type": payload.cta_type,
    }

    try:
        crow = db.execute(insert_campaign, campaign_params).mappings().first()
        if not crow:
            db.rollback()
            raise HTTPException(status_code=500, detail="Campaign insert returned no row")

        cid = crow["campaign_id"]
        audience_params = {
            "campaign_id": cid,
            "age": payload.audience_age,
            "gender": payload.audience_gender,
            "location": payload.audience_location,
            "interests": payload.audience_interests,
            "audience_temperature": payload.audience_temperature,
            "customer_type": payload.customer_type,
            "career": payload.career,
        }
        arow = db.execute(insert_audience, audience_params).mappings().first()
        if not arow:
            db.rollback()
            raise HTTPException(status_code=500, detail="Audience insert returned no row")

        adrow = db.execute(
            insert_ad,
            {"campaign_id": cid, "cta_type": payload.cta_type},
        ).mappings().first()
        if not adrow:
            db.rollback()
            raise HTTPException(status_code=500, detail="Ad insert returned no row")

        db.commit()
        out = dict(crow)
        out["audience_id"] = arow["audience_id"]
        out["ad_id"] = adrow["ad_id"]
        return out
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:  # noqa: BLE001
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=str(exc).strip() or "Database error while saving campaign or audience",
        ) from exc
