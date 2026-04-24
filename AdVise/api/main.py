from fastapi import FastAPI
from routes.route1 import router as employees_router
from routes.route2 import router as core_router
from routes.routen import router as ext_router
from routes.campaigns import router as campaigns_router

app = FastAPI(title="AdVise API", description="AdVise backend", version="0.1.0")

app.include_router(employees_router, prefix="/employees", tags=["employees"])
app.include_router(core_router, tags=["core"])
app.include_router(ext_router, prefix="/ext", tags=["extension"])
app.include_router(campaigns_router)


@app.get("/")
def root():
    return {"product": "AdVise", "docs": "/docs", "redoc": "/redoc"}
