"""
PENELOPE Backend - Health & Data Staleness Status Endpoint
Reports system health, database connectivity, ML model availability,
and /v1/health/data with last ingest timestamps per source and staleness flags.
"""

from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text, select, func

from apps.api.config import settings
from apps.api.database import get_db, active_db_url
from apps.api.ingestion.scheduler import scheduler, ml_predictor
from apps.api.ingestion.resilience import ingest_health
from apps.api.models import GridCell, WeatherObs, RiverObs, SensorDevice, Region

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


@router.get("/health/data")
@router.get("/v1/health/data")
def get_data_ingest_health(db: Session = Depends(get_db)):
    """
    Returns last successful ingest per source + staleness flags (Part 2 requirement).
    """
    now = datetime.utcnow()
    summary = ingest_health.get_summary()

    # Query DB row counts & latest timestamps
    cell_count = db.execute(select(func.count(GridCell.id))).scalar() or 0
    latest_weather = db.execute(select(func.max(WeatherObs.ts))).scalar()
    weather_count = db.execute(select(func.count(WeatherObs.id))).scalar() or 0
    latest_river = db.execute(select(func.max(RiverObs.ts))).scalar()
    river_count = db.execute(select(func.count(RiverObs.id))).scalar() or 0
    sensor_count = db.execute(select(func.count(SensorDevice.id))).scalar() or 0
    region_count = db.execute(select(func.count(Region.id))).scalar() or 0

    # Determine live staleness from DB timestamps if tracker was just initialized
    if latest_weather:
        weather_age_min = (now - latest_weather).total_seconds() / 60.0
        summary["weather"]["last_success"] = latest_weather.isoformat() + "Z"
        summary["weather"]["is_stale"] = weather_age_min > summary["weather"]["staleness_threshold_min"]
        summary["weather"]["status"] = "stale" if summary["weather"]["is_stale"] else "fresh"
        summary["weather"]["records_in_db"] = weather_count

    if latest_river:
        river_age_min = (now - latest_river).total_seconds() / 60.0
        summary["glofas"]["last_success"] = latest_river.isoformat() + "Z"
        summary["glofas"]["is_stale"] = river_age_min > summary["glofas"]["staleness_threshold_min"]
        summary["glofas"]["status"] = "stale" if summary["glofas"]["is_stale"] else "fresh"
        summary["glofas"]["records_in_db"] = river_count

        summary["sensor"]["last_success"] = latest_river.isoformat() + "Z"
        summary["sensor"]["is_stale"] = river_age_min > summary["sensor"]["staleness_threshold_min"]
        summary["sensor"]["status"] = "stale" if summary["sensor"]["is_stale"] else "fresh"
        summary["sensor"]["records_in_db"] = river_count

    if cell_count > 0:
        summary["terrain"]["status"] = "fresh"
        summary["terrain"]["is_stale"] = False
        summary["terrain"]["records_in_db"] = cell_count

    all_fresh = not any(s.get("is_stale", True) for s in summary.values())

    return {
        "status": "healthy" if all_fresh else "operational",
        "timestamp": now.isoformat() + "Z",
        "tagline": "Data today. Safer tomorrows.",
        "sources": summary,
        "database_totals": {
            "regions": region_count,
            "grid_cells": cell_count,
            "weather_observations": weather_count,
            "river_observations": river_count,
            "sensor_devices": sensor_count,
        }
    }
