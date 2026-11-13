"""
PENELOPE Backend - Health & System Status Endpoint
Reports database, scheduler, ML model status, and alert provider degradation flags.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from apps.api.config import settings
from apps.api.database import get_db, active_db_url
from apps.api.ingestion.scheduler import scheduler, ml_predictor

router = APIRouter(tags=["Health"])


@router.get("/healthz")
def get_system_health(db: Session = Depends(get_db)):
    # Database test
    db_healthy = False
    try:
        db.execute(text("SELECT 1"))
        db_healthy = True
    except Exception:
        db_healthy = False

    return {
        "status": "healthy" if db_healthy else "degraded",
        "tagline": "Data today. Safer tomorrows.",
        "pillars": ["Predict", "Prepare", "Protect"],
        "database": {
            "status": "connected" if db_healthy else "disconnected",
            "url_type": "sqlite" if "sqlite" in active_db_url else "postgresql_postgis",
        },
        "scheduler": {
            "running": scheduler.running,
            "jobs_count": len(scheduler.get_jobs()) if scheduler.running else 0,
            "sensor_simulation_active": settings.SIMULATE_SENSORS,
        },
        "ml_engine": {
            "tabular_model_loaded": ml_predictor.tabular_model is not None,
            "baseline_model_loaded": ml_predictor.baseline_model is not None,
            "lstm_model_loaded": ml_predictor.lstm_model is not None,
        },
        "alert_providers": {
            "twilio_sms": "configured" if settings.is_twilio_configured else "disabled_graceful",
            "telegram_bot": "configured" if settings.is_telegram_configured else "disabled_graceful",
            "smtp_email": "configured" if settings.is_smtp_configured else "disabled_graceful",
            "webhook": "configured" if settings.is_webhook_configured else "disabled_graceful",
        },
        "official_disclaimer": "Advisory only. Experimental AI flash-flood prediction. Follow official IMD/CWC/NDMA warnings."
    }
