"""Core / misc routes (add more groups here)."""
from fastapi import APIRouter

router = APIRouter()


@router.get("/status")
def service_status():
    """Lightweight liveness for the API container."""
    return {"product": "AdVise", "component": "api", "ok": True}
