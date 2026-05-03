from fastapi import FastAPI

from database import verify_database_connection
from routes.route2 import router as core_router
from routes.routen import router as ext_router
from routes.campaigns import router as campaigns_router
from routes.ads import router as ads_router
from routes.audience import router as audience_router
from routes.predictions import router as predictions_router
from routes.training_dataset import router as training_dataset_router
from routes.meta import router as meta_router
from routes.predictions_preview import router as predictions_preview_router
from routes.campaigns_v1 import router as campaigns_v1_router
from routes.ads_v1 import router as ads_v1_router
from routes.audience_v1 import router as audience_v1_router
from routes.predictions_v1 import router as predictions_v1_router


app = FastAPI(title="AdVise API", description="AdVise backend", version="0.1.0")


@app.on_event("startup")
def _verify_postgres_matches_etl() -> None:
    """Same Postgres `etl_db` seeds (see compose `depends_on: etl_db`)."""
    verify_database_connection()


app.include_router(core_router, tags=["core"])
app.include_router(ext_router, prefix="/ext", tags=["extension"])
app.include_router(campaigns_router)
app.include_router(ads_router)
app.include_router(audience_router)
app.include_router(predictions_router)
app.include_router(training_dataset_router)
app.include_router(meta_router)
app.include_router(predictions_preview_router)
app.include_router(campaigns_v1_router)
app.include_router(ads_v1_router)
app.include_router(audience_v1_router)
app.include_router(predictions_v1_router)


@app.get("/")
def root():
    return {"product": "AdVise", "docs": "/docs", "redoc": "/redoc"}
