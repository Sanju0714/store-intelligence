from fastapi import FastAPI

from app.database import engine
from app.database import Base

from app.ingestion import router as ingestion_router

from app.metrics import router as metrics_router

from app.health import router as health_router

from app.funnel import router as funnel_router

from app.heatmap import router as heatmap_router

from app.anomalies import router as anomalies_router
# ==========================================
# CREATE DATABASE TABLES
# ==========================================
Base.metadata.create_all(bind=engine)

# ==========================================
# FASTAPI APP
# ==========================================
app = FastAPI(
    title="Store Intelligence API"
)

# ==========================================
# ROUTERS
# ==========================================
app.include_router(ingestion_router)

app.include_router(metrics_router)

app.include_router(health_router)

app.include_router(funnel_router)

app.include_router(heatmap_router)

app.include_router(anomalies_router)
# ==========================================
# ROOT ENDPOINT
# ==========================================
@app.get("/")
def root():

    return {

        "message": "API Running",

        "status": "healthy"
    }