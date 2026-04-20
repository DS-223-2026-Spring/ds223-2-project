from fastapi import APIRouter

router = APIRouter(prefix="/campaigns")

# Dummy storage
campaigns = []
current_id = 1


# GET all campaigns
@router.get("/")
def get_campaigns():
    return campaigns


# GET one campaign
@router.get("/{campaign_id}")
def get_campaign(campaign_id: int):
    for c in campaigns:
        if c["id"] == campaign_id:
            return c
    return {"error": "Campaign not found"}


# POST create campaign
@router.post("/")
def create_campaign(data: dict):
    global current_id
    new_campaign = {"id": current_id, **data}
    campaigns.append(new_campaign)
    current_id += 1
    return new_campaign


# PUT update campaign
@router.put("/{campaign_id}")
def update_campaign(campaign_id: int, data: dict):
    for c in campaigns:
        if c["id"] == campaign_id:
            c.update(data)
            return c
    return {"error": "Campaign not found"}


# DELETE campaign
@router.delete("/{campaign_id}")
def delete_campaign(campaign_id: int):
    for c in campaigns:
        if c["id"] == campaign_id:
            campaigns.remove(c)
            return {"message": "Deleted"}
    return {"error": "Campaign not found"}
