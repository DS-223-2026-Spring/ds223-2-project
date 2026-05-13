from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from meta_dataset import enums_from_training_dataset, merge_with_fallback
from schema import MetaEnumsResponse
from training_vocab import (
    POOL_AUD_TEMPS,
    POOL_CTAS,
    POOL_CUSTOMERS,
    POOL_INTENTS,
    POOL_PRODUCT_TYPES,
)

router = APIRouter(prefix="/v1/meta", tags=["meta"])


def _static_enums() -> dict[str, list[str]]:
    """Pools aligned with preprocessing / CSV when DB has no rows yet."""
    return {
        "platforms": ["facebook", "instagram", "google", "tiktok", "youtube"],
        "campaign_intents": list(POOL_INTENTS),
        "cta_types": list(POOL_CTAS),
        "audience_temperature": list(POOL_AUD_TEMPS),
        "devices": ["mobile", "desktop", "tablet"],
        "customer_types": list(POOL_CUSTOMERS),
        "product_types": list(POOL_PRODUCT_TYPES),
        "regions": ["US", "UK", "India", "Canada", "Germany", "France", "Armenia"],
        "age_bands": ["18-24", "25-34", "35-44", "45-54", "55+"],
        "genders": ["male", "female"],
        "interests": [
            "tech",
            "fashion",
            "food",
            "sports",
            "travel",
            "music",
            "fitness",
            "finance",
            "gaming",
            "beauty",
        ],
        "careers": [
            "student",
            "professional",
            "entrepreneur",
            "freelancer",
            "manager",
            "engineer",
            "teacher",
            "healthcare",
            "other",
        ],
    }


@router.get("/enums", response_model=MetaEnumsResponse)
def get_enums(db: Session = Depends(get_db)):
    """
    Dropdown values sourced from DISTINCT ``training_dataset`` columns when available,
    so the frontend matches vocabulary the tier models saw during training.
    """
    collected = enums_from_training_dataset(db)
    merged = merge_with_fallback(collected, _static_enums)
    return MetaEnumsResponse(
        platforms=merged["platforms"],
        campaign_intents=merged["campaign_intents"],
        cta_types=merged["cta_types"],
        audience_temperature=merged["audience_temperature"],
        devices=merged["devices"],
        customer_types=merged["customer_types"],
        product_types=merged["product_types"],
        regions=merged["regions"],
        age_bands=merged["age_bands"],
        genders=merged["genders"],
        interests=merged["interests"],
        careers=merged["careers"],
    )
