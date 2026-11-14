"""
PENELOPE Backend - APScheduler Ingestion & Risk Intelligence Jobs
Automates:
- Weather ingestion every 30 min (Open-Meteo)
- River ingestion every 3 hours (GloFAS Flood API)
- Simulated sensor readings (correlating with rainfall)
- Real-time ML risk re-evaluation
"""

import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy import select

from apps.api.config import settings
from apps.api.database import SessionLocal
from apps.api.models import Region
from apps.api.ingestion.terrain import terrain_pipeline
from apps.api.ingestion.weather import weather_service
from apps.api.ingestion.river import river_service
from app.sim.sensors import run_sensor_simulation
from ml.predictor import FloodRiskPredictor

logger = logging.getLogger("penelope.scheduler")

scheduler = AsyncIOScheduler()
ml_predictor = FloodRiskPredictor(model_dir=settings.MODEL_DIR)

# In-memory event buffer for WebSocket broadcasting
latest_broadcast_events = []


async def run_weather_ingestion_job():
    """Scheduled job: runs every 30 minutes."""
    logger.info("Executing scheduled weather ingestion job (every 30m)...")
    with SessionLocal() as db:
        regions = db.execute(select(Region)).scalars().all()
        for r in regions:
            try:
                await weather_service.ingest_weather_for_region(r, db)
            except Exception as e:
                logger.error(f"Weather ingestion failed for {r.name}: {e}")


async def run_river_ingestion_job():
    """Scheduled job: runs every 3 hours."""
    logger.info("Executing scheduled river GloFAS ingestion job (every 3h)...")
    with SessionLocal() as db:
        regions = db.execute(select(Region)).scalars().all()
        for r in regions:
            try:
                await river_service.ingest_river_for_region(r, db)
            except Exception as e:
                logger.error(f"River GloFAS ingestion failed for {r.name}: {e}")


async def run_sensor_simulation_cycle():
    """Scheduled job: runs every 5 minutes if SIMULATE_SENSORS is enabled."""
    if not settings.SIMULATE_SENSORS:
        return
    try:
        run_sensor_simulation(num_steps=1)
    except Exception as e:
        logger.error(f"Sensor simulation cycle failed: {e}")


def start_scheduler():
    if scheduler.running:
        return

    # Add jobs per requirements:
    # 1. Weather ingestion: every 30 minutes
    scheduler.add_job(
        run_weather_ingestion_job,
        trigger=IntervalTrigger(minutes=30),
        id="weather_ingestion_30m",
        name="Open-Meteo Weather Ingestion",
        replace_existing=True
    )

    # 2. River ingestion: every 3 hours
    scheduler.add_job(
        run_river_ingestion_job,
        trigger=IntervalTrigger(hours=3),
        id="river_ingestion_3h",
        name="GloFAS River Discharge Ingestion",
        replace_existing=True
    )

    # 3. Simulated sensors: every 2 minutes
    scheduler.add_job(
        run_sensor_simulation_cycle,
        trigger=IntervalTrigger(minutes=2),
        id="sensor_sim_cycle",
        name="Simulated Sensor Telemetry",
        replace_existing=True
    )

    scheduler.start()
    logger.info("APScheduler started with Part 2 ingestion jobs.")


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("APScheduler stopped.")
