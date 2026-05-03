"""Core / misc routes (add more groups here)."""
from fastapi import APIRouter
from schema import StatusResponse

router = APIRouter()


@router.get("/status")
def service_status():
    return {"product": "AdVise", "component": "api", "ok": True}


@router.get("/v1/status", response_model=StatusResponse)
def v1_status():
    """
    Return backend health information and basic runtime limits.
    """
    return {
        "status": "ok",
        "backend": "connected",
        "model_version": "v1-placeholder",
        "max_creatives": 3,
        "upload_limits": {
            "max_file_size_mb": 10,
            "allowed_types": ["png", "jpg", "jpeg", "pdf"]
        },
        "prefect_available": False
    }