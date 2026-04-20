from fastapi import FastAPI
from app.routers.health import router as health_router
from app.routers.campaigns import router as campaigns_router

app = FastAPI()

app.include_router(health_router)
app.include_router(campaigns_router)

@app.get("/")
def root():
    return {"message": "Backend is running"}
