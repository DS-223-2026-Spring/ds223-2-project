from fastapi import APIRouter, HTTPException
from app.schemas.campaign import CampaignCreate, CampaignUpdate, CampaignResponse

router = APIRouter(prefix="/campaigns", tags=["campaigns"])

# Dummy storage
campaigns = []
current_id = 1


# GET all campaigns
@router.get("/", response_model=list[CampaignResponse])
def get_campaigns():
    return campaigns


# GET one campaign
@router.get("/{campaign_id}", response_model=CampaignResponse)
def get_campaign(campaign_id: int):
    for c in campaigns:
        if c["id"] == campaign_id:
            return c
    raise HTTPException(status_code=404, detail="Campaign not found")


# POST create campaign
@router.post("/", response_model=CampaignResponse)
def create_campaign(data: CampaignCreate):
    global current_id
    new_campaign = {"id": current_id, **data.model_dump()}
    campaigns.append(new_campaign)
    current_id += 1
    return new_campaign


# PUT update campaign
@router.put("/{campaign_id}", response_model=CampaignResponse)
def update_campaign(campaign_id: int, data: CampaignUpdate):
    for c in campaigns:
        if c["id"] == campaign_id:
            update_data = data.model_dump(exclude_unset=True)
            c.update(update_data)
            return c
    raise HTTPException(status_code=404, detail="Campaign not found")


# DELETE campaign
@router.delete("/{campaign_id}")
def delete_campaign(campaign_id: int):
    for c in campaigns:
        if c["id"] == campaign_id:
            campaigns.remove(c)
            return {"message": "Deleted"}
    raise HTTPException(status_code=404, detail="Campaign not found")
