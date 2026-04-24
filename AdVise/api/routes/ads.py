from fastapi import APIRouter
from schema import AdCreate, AdResponse

router = APIRouter(prefix="/ads", tags=["Ads"])

ads = {
    1: {"campaign_id": 1, "platform": "Instagram", "creative_type": "Video"}
}

@router.get("/", response_model=dict[int, AdResponse])
def get_ads():
    return {
        ad_id: {"id": ad_id, **ad}
        for ad_id, ad in ads.items()
    }

@router.post("/", response_model=AdResponse)
def create_ad(ad: AdCreate):
    new_id = max(ads.keys()) + 1 if ads else 1
    ads[new_id] = ad.model_dump()
    return {"id": new_id, **ads[new_id]}