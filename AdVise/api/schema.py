from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

# ── Legacy HR demo models (older routes); not aligned with marketing schema.sql ──


class Employee(BaseModel):
    employee_id: int
    first_name: str
    last_name: str
    email: str
    salary: int

    class Config:
        orm_mode = True


class EmployeeCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    salary: int


# ── Legacy CRUD-shaped marketing placeholders (routes may return raw SQL, not these) ──


class CampaignBase(BaseModel):
    name: str
    budget: float
    platform: str


class CampaignCreate(CampaignBase):
    pass


class CampaignResponse(CampaignBase):
    id: int


class AdBase(BaseModel):
    campaign_id: int
    platform: str
    creative_type: str


class AdCreate(AdBase):
    pass


class AdResponse(AdBase):
    id: int


class AudienceBase(BaseModel):
    age: str
    gender: str
    location: str
    interests: str


class AudienceCreate(AudienceBase):
    pass


class AudienceResponse(AudienceBase):
    id: int


class PredictionBase(BaseModel):
    campaign_id: int
    predicted_ctr: float
    predicted_conversion_rate: float


class PredictionCreate(PredictionBase):
    pass


class PredictionResponse(PredictionBase):
    id: int


class TrainingDatasetBase(BaseModel):
    platform: str
    budget: float
    duration_days: int
    ctr: float
    conversion_rate: float


class TrainingDatasetCreate(TrainingDatasetBase):
    pass


class TrainingDatasetResponse(TrainingDatasetBase):
    id: int


# ── v1 contract DTOs (authoritative for /v1/* documented endpoints) ──


class MetaEnumsResponse(BaseModel):
    platforms: List[str]
    campaign_intents: List[str]
    cta_types: List[str]
    audience_temperature: List[str]
    devices: List[str]
    customer_types: List[str]
    product_types: List[str]
    regions: List[str]
    age_bands: List[str]


class StatusResponse(BaseModel):
    status: str
    backend: str
    model_version: str
    max_creatives: int
    upload_limits: Dict[str, Any]
    prefect_available: bool


class PredictionPreviewRequest(BaseModel):
    platform: str
    campaign_intent: str
    product_type: str
    cta_type: str
    audience_temperature: str
    customer_type: str
    budget: float
    duration_days: int
    creative_count: Optional[int] = 1
    # Optional demographics (prefer training_dataset vocabulary; omit → safe defaults below)
    audience_age: Optional[str] = Field(default=None, description="e.g. 25-34")
    audience_gender: Optional[str] = Field(default=None, description="male / female")
    audience_location: Optional[str] = Field(default=None)
    audience_interests: Optional[str] = Field(default=None)
    career: Optional[str] = Field(default=None)
    # First creative as standard base64 (no data: URL prefix). Runs DS image extraction in API when set.
    creative_image_base64: Optional[str] = None


class RecommendationBlock(BaseModel):
    rank: int
    primary_kpi: str
    score: float
    hint: str


class PredictionPreviewResponse(BaseModel):
    run_id: str
    status: str
    model_version: str
    campaign_intent: str
    target_metric: str
    target_label: str
    predicted_tier: Optional[str] = None
    prediction_confidence: Optional[float] = None
    recommendations: List[RecommendationBlock]
    input_summary: Dict[str, Any]
    creative_features: Optional[Dict[str, Any]] = None
    model_feature_snapshot: Optional[Dict[str, Any]] = None


class PredictionRunResponse(PredictionPreviewResponse):
    pass
