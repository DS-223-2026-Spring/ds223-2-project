from fastapi import APIRouter, HTTPException
from schema import CampaignCreate, CampaignResponse

router = APIRouter(prefix="/campaigns", tags=["Campaigns"])

campaigns = {
    1: {"name": "Test Campaign", "budget": 1000.0, "platform": "Instagram"}
}

@router.get("/", response_model=dict[int, CampaignResponse])
def get_campaigns():
    return {
        campaign_id: {"id": campaign_id, **campaign}
        for campaign_id, campaign in campaigns.items()
    }

@router.get("/{campaign_id}", response_model=CampaignResponse)
def get_campaign(campaign_id: int):
    if campaign_id not in campaigns:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return {"id": campaign_id, **campaigns[campaign_id]}

@router.post("/", response_model=CampaignResponse)
def create_campaign(campaign: CampaignCreate):
    new_id = max(campaigns.keys()) + 1 if campaigns else 1
    campaigns[new_id] = campaign.model_dump()
    return {"id": new_id, **campaigns[new_id]}

@router.put("/{campaign_id}", response_model=CampaignResponse)
def update_campaign(campaign_id: int, campaign: CampaignCreate):
    if campaign_id not in campaigns:
        raise HTTPException(status_code=404, detail="Campaign not found")
    campaigns[campaign_id] = campaign.model_dump()
    return {"id": campaign_id, **campaigns[campaign_id]}

@router.delete("/{campaign_id}")
def delete_campaign(campaign_id: int):
    if campaign_id not in campaigns:
        raise HTTPException(status_code=404, detail="Campaign not found")
    deleted = campaigns.pop(campaign_id)
    return {"message": "Campaign deleted", "deleted": deleted}