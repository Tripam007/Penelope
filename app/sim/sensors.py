"""
PENELOPE Backend - River Sensor Simulation CLI (python -m app.sim.sensors)
Generates physically plausible river gauge telemetry correlated with real antecedent rainfall.
Hard Rule 3 Compliance: Always marks records with source="simulated" and [SIM] badge.
"""

import sys
import math
import random
import logging
from datetime import datetime, timedelta
from sqlalchemy import select, func
from apps.api.database import SessionLocal
from apps.api.models import SensorDevice, RiverObs, WeatherObs
from apps.api.ingestion.resilience import ingest_health

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("penelope.sim.sensors")


def run_sensor_simulation(num_steps: int = 1):
    """
    Simulates water level and discharge readings for all registered simulated sensors.
    Correlates stage height with recent precipitation in the basin.
    """
    logger.info("Running river-gauge IoT sensor simulation...")
    with SessionLocal() as db:
        sensors = db.execute(
            select(SensorDevice).where(
                (SensorDevice.is_simulated.is_(True)) | (SensorDevice.status == "online")
            )
        ).scalars().all()

        if not sensors:
            logger.info("No sensors found in database. Auto-creating demo simulated sensors...")
            from apps.api.models import Region
            regions = db.execute(select(Region)).scalars().all()
            for r in regions:
                s = SensorDevice(
                    sensor_code=f"SIM-GAUGE-{r.name.split('-')[0].upper()}-01",
                    name=f"{r.name.split('-')[0]} River Level Radar Gauge",
                    geom={"type": "Point", "coordinates": [r.center_lon, r.center_lat]},
                    api_key_hash="default-hash",
                    river_name=f"{r.name.split('-')[0]} River",
                    warning_level_m=3.5,
                    danger_level_m=5.0,
                    is_simulated=True,
                    region_id=r.id,
                    status="online"
                )
                db.add(s)
            db.commit()
            sensors = db.execute(select(SensorDevice)).scalars().all()

        created_count = 0
        now = datetime.utcnow()

        for step in range(num_steps):
            step_time = now - timedelta(minutes=(num_steps - 1 - step) * 15)

            for sensor in sensors:
                # Query recent rainfall in this basin to correlate discharge
                recent_rain = 0.0
                if sensor.region_id:
                    rain_val = db.execute(
                        select(func.avg(WeatherObs.rain_3h_mm)).where(WeatherObs.basin_id == sensor.region_id)
                    ).scalar()
                    recent_rain = float(rain_val or 0.0)

                # Base stage height
                base_level = sensor.warning_level_m * 0.45
                rain_runoff_boost = min(3.5, recent_rain * 0.18)
                wave = 0.15 * math.sin((step_time.hour + step_time.minute / 60.0) * math.pi / 12.0)
                noise = random.uniform(-0.04, 0.04)

                water_level = round(max(0.6, base_level + rain_runoff_boost + wave + noise), 2)
                rate_of_rise = round((recent_rain * 0.03) + random.uniform(-0.02, 0.05), 3)
                
                # Rating curve Q = a * h^b
                discharge = round(max(3.0, 10.5 * math.pow(water_level, 1.4)), 1)

                reading = RiverObs(
                    station_or_cell_id=sensor.sensor_code,
                    sensor_id=sensor.id,
                    ts=step_time,
                    timestamp=step_time,
                    level_m=water_level,
                    water_level_m=water_level,
                    rate_of_rise_mh=rate_of_rise,
                    discharge_m3s=discharge,
                    discharge_rate_m3s=discharge,
                    source="simulated"  # Strictly marked simulated per Hard Rule 3
                )
                db.add(reading)
                sensor.last_seen = step_time
                created_count += 1

        db.commit()
        logger.info(f"Successfully generated {created_count} simulated river-gauge readings.")
        ingest_health.record_run("sensor", created_count)
        return created_count


if __name__ == "__main__":
    count = run_sensor_simulation(num_steps=3)
    print(f"Generated {count} simulated sensor telemetry records.")
