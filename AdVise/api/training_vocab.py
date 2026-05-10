"""
Values that appear (or SHOULD appear when normalized) in `training_dataset`,
aligned with ``AdVise/etl/db/scripts/preprocessing.py`` pools.
"""

from campaign_intent import normalize_intent

POOL_INTENTS = ("sales", "awareness", "traffic", "leads", "engagement")
POOL_PRODUCT_TYPES = (
    "electronics",
    "fashion",
    "food",
    "beauty",
    "fitness",
    "finance",
    "travel",
    "education",
    "home",
    "software",
)
POOL_CTAS = ("buy_now", "learn_more", "sign_up", "go_to_page")
POOL_AUD_TEMPS = ("cold", "warm", "hot")
POOL_CUSTOMERS = ("new", "returning")
POOL_PLATFORMS = ("facebook", "instagram", "google", "tiktok", "youtube")

INTENT_TO_MODEL_LABEL: dict[str, str] = {
    "conversion": "leads",
    "lead_generation": "leads",
}


def _nearest_pool(value: str, pool: tuple[str, ...]) -> str:
    v = normalize_intent(value).replace(" ", "_")
    if v in pool:
        return v
    for p in pool:
        if v in p or p in v:
            return p
    return pool[0]


def canonical_platform(value: str) -> str:
    k = normalize_intent(value).replace(" ", "_")
    if k in POOL_PLATFORMS:
        return k
    aliases = {"google_ads": "google", "youtube_ads": "youtube", "meta": "facebook"}
    if k in aliases:
        return aliases[k]
    return _nearest_pool(k, POOL_PLATFORMS)


def canonical_campaign_intent(user_intent: str) -> str:
    """Label stored in ``feature_row["campaign_intent"]`` for encoders/models."""
    k = normalize_intent(user_intent)
    if k in INTENT_TO_MODEL_LABEL:
        return INTENT_TO_MODEL_LABEL[k]
    if k in POOL_INTENTS:
        return k
    return "engagement"


def canonical_product_type(value: str) -> str:
    return _nearest_pool(value, POOL_PRODUCT_TYPES)


def canonical_cta_type(value: str) -> str:
    raw = normalize_intent(value).replace(" ", "_")
    ux = raw.replace("-", "_")
    if ux in POOL_CTAS:
        return ux
    lowered = raw.replace("_", "")
    mapping = {
        "shopnow": "buy_now",
        "learnmore": "learn_more",
        "signup": "sign_up",
        "gotopage": "go_to_page",
        "buynow": "buy_now",
    }
    if lowered in mapping:
        return mapping[lowered]
    return POOL_CTAS[0]


def canonical_audience_temperature(value: str) -> str:
    k = normalize_intent(value)
    if k in POOL_AUD_TEMPS:
        return k
    return POOL_AUD_TEMPS[0]


def canonical_customer_type(value: str) -> str:
    k = normalize_intent(value).replace("-", "")
    if k in POOL_CUSTOMERS:
        return k
    return POOL_CUSTOMERS[0]
