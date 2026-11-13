"""
PENELOPE Backend - River-Gauge Sensor Telemetry & Ingestion Endpoints (Hard Rule 3)
"""

from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select

from apps.api.database import get_db
from apps.api.models import Sensor, SensorReading
from apps.api.schemas import SensorIngestRequest, SensorReadingResponse, SensorResponse

router = APIRouter(prefix="/sensors", tags=["Sensors"])


@router.post("/ingest", response_model=SensorReadingResponse)
def ingest_sensor_reading(payload: SensorIngestRequest, db: Session = Depends(get_db)):
    """
    Real river-gauge sensor telemetry ingest endpoint.
    Accepts live hardware gauge readings or simulated readings.
    Every simulated reading carries source='simulated' per Hard Rule 3.
    """
    sensor = db.execute(select(Sensor).where(Sensor.sensor_code == payload.sensor_code)).scalars().first()
    if not sensor:
        raise HTTPException(status_code=404, detail=f"Sensor '{payload.sensor_code}' not registered.")

    reading = SensorReading(
        sensor_id=sensor.id,
        timestamp=payload.timestamp or datetime.utcnow(),
        water_level_m=payload.water_level_m,
        rate_of_rise_mh=payload.rate_of_rise_mh or 0.0,
        discharge_rate_m3s=payload.discharge_rate_m3s or 0.0,
        source=payload.source  # "live" or "simulated"
    )
    db.add(reading)
    sensor.status = "online"
    db.commit()
    db.refresh(reading)
    return reading


@router.get("", response_model=List[SensorResponse])
def list_sensors(basin_id: str = None, db: Session = Depends(get_db)):
    stmt = select(Sensor)
    if basin_id:
        stmt = stmt.where(Sensor.basin_id == basin_id)
    sensors = db.execute(stmt).scalars().all()

    results = []
    for s in sensors:
        latest = (
            db.execute(
                select(SensorReading)
                .where(SensorReading.sensor_id == s.id)
                .order_by(SensorReading.timestamp.desc())
                .limit(1)
            )
            .scalars()
            .first()
        )
        s_dict = {
            "id": s.id,
            "basin_id": s.basin_id,
            "sensor_code": s.sensor_code,
            "name": s.name,
            "river_name": s.river_name,
            "lat": s.lat,
            "lon": s.lon,
            "warning_level_m": s.warning_level_m,
            "danger_level_m": s.danger_level_m,
            "is_simulated": s.is_simulated,
            "status": s.status,
            "latest_reading": latest,
        }
        results.append(s_dict)
    return results


@router.get("/{sensor_code}/readings", response_model=List[SensorReadingResponse])
def get_sensor_readings(
    sensor_code: str,
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
):
    sensor = db.execute(select(Sensor).where(Sensor.sensor_code == sensor_code)).scalars().first()
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")

    readings = (
        db.execute(
            select(SensorReading)
            .where(SensorReading.sensor_id == sensor.id)
            .order_by(SensorReading.timestamp.desc())
            .limit(limit)
        )
        .scalars()
        .all()
    )
    return readings


@router.post("/simulate-surge")
def trigger_simulated_cloudburst_surge(sensor_code: str, db: Session = Depends(get_db)):
    """
    On-demand simulation tool: triggers a rapid mountain river surge on a simulated sensor
    to test early-warning alert propagation. Strictly marked source="simulated".
    """
    sensor = db.execute(select(Sensor).where(Sensor.sensor_code == sensor_code)).scalars().first()
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")

    surged_level = round(sensor.danger_level_m * 1.08, 2)
    reading = SensorReading(
        sensor_id=sensor.id,
        timestamp=datetime.utcnow(),
        water_level_m=surged_level,
        rate_of_rise_mh=0.85,
        discharge_rate_m3s=95.0,
        source="simulated"  # Strictly marked simulated
    )
    db.add(reading)
    db.commit()
    db.refresh(reading)

    return {
        "status": "surge_triggered",
        "sensor_code": sensor.sensor_code,
        "water_level_m": surged_level,
        "danger_level_m": sensor.danger_level_m,
        "source": "simulated",
        "sim_badge": True,
        "notice": "This reading is SIMULATED and labeled accordingly."
    }

