from fastapi import APIRouter

from schema import AudienceCreate, AudienceResponse

router = APIRouter(prefix="/audience", tags=["Audience"])

audience = {

    1: {

        "age": 25,

        "gender": "female",

        "location": "Yerevan",

        "interests": "technology"

    }

}

@router.get("/", response_model=dict[int, AudienceResponse])

def get_audience():

    return {

        audience_id: {"id": audience_id, **item}

        for audience_id, item in audience.items()

    }

@router.post("/", response_model=AudienceResponse)

def create_audience(item: AudienceCreate):

    new_id = max(audience.keys()) + 1 if audience else 1

    audience[new_id] = item.model_dump()

    return {"id": new_id, **audience[new_id]}