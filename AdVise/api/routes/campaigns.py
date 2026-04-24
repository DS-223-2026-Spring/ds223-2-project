from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/campaigns", tags=["Campaigns"])

class Campaign(BaseModel):
    name: str
    budget: float
    platform: str

# Dummy in-memory data
campaigns = {
    1: {"name": "Test Campaign", "budget": 1000.0, "platform": "Instagram"}
}

@router.get("/")
def get_campaigns():
    return campaigns

@router.get("/{campaign_id}")
def get_campaign(campaign_id: int):
    if campaign_id not in campaigns:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaigns[campaign_id]

@router.post("/")
def create_campaign(campaign: Campaign):
    new_id = max(campaigns.keys()) + 1 if campaigns else 1
    campaigns[new_id] = campaign.model_dump()
    return {"id": new_id, "campaign": campaigns[new_id]}

@router.put("/{campaign_id}")
def update_campaign(campaign_id: int, campaign: Campaign):
    if campaign_id not in campaigns:
        raise HTTPException(status_code=404, detail="Campaign not found")
    campaigns[campaign_id] = campaign.model_dump()
    return {"id": campaign_id, "campaign": campaigns[campaign_id]}

@router.delete("/{campaign_id}")
def delete_campaign(campaign_id: int):
    if campaign_id not in campaigns:
        raise HTTPException(status_code=404, detail="Campaign not found")
    deleted = campaigns.pop(campaign_id)
    return {"message": "Campaign deleted", "deleted": deleted}