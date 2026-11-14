"""
PENELOPE Backend - Unified Ingestion CLI (make ingest)
Executes:
1. Terrain pipeline: generates 500m grid cells, elevation, slope, aspect, flow accumulation, TWI for all regions.
2. Weather ingestion: Open-Meteo forecasts for all regions.
3. River GloFAS ingestion: discharge forecasts for all regions.
4. Simulated sensor telemetry correlated with rainfall.
Idempotent and resumable.
"""

import sys
import asyncio
import logging
from sqlalchemy import select

from apps.api.database import init_db, SessionLocal
from apps.api.models import Region
from apps.api.ingestion.terrain import terrain_pipeline
from apps.api.ingestion.weather import weather_service
from apps.api.ingestion.river import river_service
from app.sim.sensors import run_sensor_simulation

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("penelope.ingestion.cli")


async def main():
    logger.info("=================================================================")
    logger.info("PENELOPE: Executing PART 2 Ingestion Pipeline (make ingest)")
    logger.info("Data today. Safer tomorrows. | Predict · Prepare · Protect")
    logger.info("=================================================================")

    init_db()

    with SessionLocal() as db:
        regions = db.execute(select(Region)).scalars().all()
        if not regions:
            logger.error("No regions found! Run 'make seed' first.")
            sys.exit(1)

        logger.info(f"Discovered {len(regions)} seeded regions: {[r.name for r in regions]}")

        # 1. Terrain Pipeline
        logger.info("--- Step 1: Processing Terrain Grids & Topographic Features ---")
        total_cells = 0
        for r in regions:
            cells_count = await terrain_pipeline.process_region(r, db, res_m=500.0)
            total_cells += cells_count
        logger.info(f"Total grid cells active: {total_cells}")

        # 2. Weather Ingestion
        logger.info("--- Step 2: Ingesting Real Open-Meteo Weather Observations ---")
        total_weather = 0
        for r in regions:
            w_count = await weather_service.ingest_weather_for_region(r, db)
            total_weather += w_count
        logger.info(f"Total weather records ingested: {total_weather}")

        # 3. River GloFAS Ingestion
        logger.info("--- Step 3: Ingesting GloFAS River Discharges ---")
        total_river = 0
        for r in regions:
            rv_count = await river_service.ingest_river_for_region(r, db)
            total_river += rv_count
        logger.info(f"Total GloFAS river records ingested: {total_river}")

        # 4. Sensor Simulation
        logger.info("--- Step 4: Generating Rainfall-Correlated Sensor Telemetry ---")
        sim_count = run_sensor_simulation(num_steps=3)
        logger.info(f"Total sensor readings recorded: {sim_count}")

    logger.info("=================================================================")
    logger.info("PART 2 Ingestion Pipeline Complete! All datasets fresh and live.")
    logger.info("=================================================================")


if __name__ == "__main__":
    asyncio.run(main())

