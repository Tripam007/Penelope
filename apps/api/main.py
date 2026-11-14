"""
PENELOPE Backend - FastAPI Application Entrypoint
Tagline: "Data today. Safer tomorrows."
Pillars: Predict · Prepare · Protect
"""

import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from apps.api.config import settings
from apps.api.database import init_db
from apps.api.seed import seed_database
from apps.api.ingestion.scheduler import start_scheduler, stop_scheduler

from apps.api.routes.health import router as health_router
from apps.api.routes.map import router as map_router
from apps.api.routes.villages import router as villages_router
from apps.api.routes.sensors import router as sensors_router
from apps.api.routes.alerts import router as alerts_router
from apps.api.routes.ml_insights import router as ml_router
from apps.api.routes.websockets import router as ws_router
from apps.api.auth.router import router as auth_router
from apps.api.middleware import RequestIdMiddleware

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("penelope.api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing PENELOPE database and seed data...")
    init_db()
    seed_database()

    if os.getenv("TESTING") != "true":
        logger.info("Starting background ingestion scheduler & sensor simulation daemon...")
        start_scheduler()
    yield
    if os.getenv("TESTING") != "true":
        logger.info("Shutting down background services...")
        stop_scheduler()


app = FastAPI(
    title="PENELOPE API - Flash-Flood Prediction & Early-Warning Platform",
    description="AI-powered flash-flood prediction and early-warning platform for hilly terrain (Himalayas / Western Ghats). Tagline: 'Data today. Safer tomorrows.' Pillars: Predict · Prepare · Protect.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestIdMiddleware)

# Include API routers under /api/v1
app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
app.include_router(health_router, prefix=settings.API_V1_PREFIX)
app.include_router(map_router, prefix=settings.API_V1_PREFIX)
app.include_router(villages_router, prefix=settings.API_V1_PREFIX)
app.include_router(sensors_router, prefix=settings.API_V1_PREFIX)
app.include_router(alerts_router, prefix=settings.API_V1_PREFIX)
app.include_router(ml_router, prefix=settings.API_V1_PREFIX)
app.include_router(ws_router, prefix=settings.API_V1_PREFIX)

app.include_router(health_router)


@app.get("/")
def root():
    return {
        "platform": "PENELOPE",
        "tagline": "Data today. Safer tomorrows.",
        "pillars": ["Predict", "Prepare", "Protect"],
        "docs_url": "/docs",
        "api_v1": settings.API_V1_PREFIX,
        "advisory": "Follow official IMD/CWC/NDMA warnings for active disaster response."
    }
