from pydantic import BaseModel


# Request schema for creating a campaign
class CampaignCreate(BaseModel):
    name: str
    budget: int


# Request schema for updating a campaign
class CampaignUpdate(BaseModel):
    name: str | None = None
    budget: int | None = None


# Response schema
class CampaignResponse(BaseModel):
    id: int
    name: str
    budget: int
