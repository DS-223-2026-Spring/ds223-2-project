"""
Placeholder for additional route groups (n-th module).
Replace or extend with your own APIRouter and endpoints.
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/placeholder")
def reserved():
    return {"message": "Extend `routen` with new domain routes when needed."}
