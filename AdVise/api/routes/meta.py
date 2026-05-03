from fastapi import APIRouter
from schema import MetaEnumsResponse

router = APIRouter(prefix="/v1/meta", tags=["meta"])

@router.get("/enums", response_model=MetaEnumsResponse)
def get_enums():
    """
    Return canonical dropdown values used by the frontend campaign form.
    """
    return {
        "platforms": ["Instagram", "Facebook", "TikTok", "YouTube", "Google Ads"],
        "campaign_intents": ["awareness", "engagement", "conversion", "lead_generation"],
        "cta_types": ["Shop Now", "Learn More", "Sign Up", "Download", "Contact Us"],
        "audience_temperature": ["cold", "warm", "hot"],
        "devices": ["mobile", "desktop", "tablet"],
        "customer_types": ["new", "returning"],
        "product_types": ["software", "service", "subscription", "physical_product"],
        "regions": ["Yerevan", "Armenia", "Europe", "North America", "Other"],
        "age_bands": ["18-24", "25-34", "35-44", "45-54", "55+"]
    }