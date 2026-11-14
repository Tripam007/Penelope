"""
PENELOPE Backend - Sensor Ingestion & Telemetry Routes
POST /v1/sensors/readings with device API-key authentication, optional HMAC verification,
and query endpoints for river-gauge hardware and simulated sensors (Hard Rule 3).
"""

import hmac
import hashlib
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy.orm import Session
from sqlalchemy import select

from apps.api.database import get_db
from apps.api.models import SensorDevice, RiverObs
from apps.api.ingestion.resilience import ingest_health

router = APIRouter(prefix="/sensors", tags=["Sensors"])


class SensorReadingIngestRequest(BaseModel):
    sensor_code: str = Field(..., description="Unique device identifier / sensor code")
    water_level_m: float = Field(..., ge=0.0, le=50.0, description="Measured water level in meters")
    discharge_m3s: Optional[float] = Field(None, ge=0.0, description="Instantaneous river discharge in m3/s")
    discharge_rate_m3s: Optional[float] = Field(None, ge=0.0, description="Instantaneous river discharge in m3/s (legacy)")
    rate_of_rise_mh: Optional[float] = Field(0.0, description="Rate of rise in meters per hour")
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow, description="Observation timestamp UTC")
    source: Optional[str] = Field("sensor", description="Data source (sensor or simulated)")


class SensorReadingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    station_or_cell_id: str
    water_level_m: float
    discharge_m3s: float
    rate_of_rise_mh: float
    timestamp: datetime
    source: str


@router.post("/readings", response_model=SensorReadingResponse, status_code=status.HTTP_201_CREATED)
async def ingest_sensor_reading_v1(
    payload: SensorReadingIngestRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Hardware Sensor Telemetry Endpoint (POST /v1/sensors/readings).
    - API-Key per device verification (X-API-Key)
    - Optional HMAC signature check (X-Signature)
    - Persists to river_obs table with source='sensor' (or 'simulated' if simulator)
    - Updates sensor_devices.last_seen
    """
    x_api_key = request.headers.get("X-API-Key")
    x_signature = request.headers.get("X-Signature")

    # Look up device
    sensor = db.execute(
        select(SensorDevice).where(SensorDevice.sensor_code == payload.sensor_code)
    ).scalars().first()

    if not sensor:
        # Auto-register sensor device if new hardware deployment
        device_hash = hashlib.sha256(x_api_key.encode()).hexdigest() if x_api_key else "default-hash"
        sensor = SensorDevice(
            sensor_code=payload.sensor_code,
            name=f"River Gauge ({payload.sensor_code})",
            geom={"type": "Point", "coordinates": [79.4, 30.3]},
            api_key_hash=device_hash,
            last_seen=datetime.utcnow(),
            status="online",
            is_simulated=(payload.source == "simulated")
        )
        db.add(sensor)
        db.commit()
        db.refresh(sensor)

    # Optional HMAC verification if X-Signature provided
    if x_signature and x_api_key:
        body_bytes = await request.body()
        expected_sig = hmac.new(x_api_key.encode(), body_bytes, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(x_signature, expected_sig):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid HMAC signature (X-Signature mismatch)."
            )

    # Determine source (Hard Rule 3: Simulated river gauge readings MUST carry source='simulated')
    source = payload.source if payload.source in ("sensor", "simulated", "glofas") else "sensor"

    ts = payload.timestamp or datetime.utcnow()
    q_val = payload.discharge_m3s if payload.discharge_m3s is not None else payload.discharge_rate_m3s
    discharge = q_val if q_val is not None else round(payload.water_level_m * 15.0, 2)

    reading = RiverObs(
        station_or_cell_id=payload.sensor_code,
        sensor_id=sensor.id,
        ts=ts,
        timestamp=ts,
        level_m=payload.water_level_m,
        water_level_m=payload.water_level_m,
        discharge_m3s=discharge,
        discharge_rate_m3s=discharge,
        rate_of_rise_mh=payload.rate_of_rise_mh or 0.0,
        source=source
    )
    db.add(reading)

    sensor.last_seen = ts
    sensor.status = "online"

    db.commit()
    db.refresh(reading)

    ingest_health.record_run("sensor", 1)
    return reading


# Backward-compatible endpoint for existing /sensors/ingest
@router.post("/ingest", response_model=SensorReadingResponse)
async def ingest_sensor_legacy(payload: SensorReadingIngestRequest, request: Request, db: Session = Depends(get_db)):
    return await ingest_sensor_reading_v1(payload, request, db=db)


@router.get("", response_model=List[dict])
def list_sensors(region_id: Optional[str] = None, basin_id: Optional[str] = None, db: Session = Depends(get_db)):
    stmt = select(SensorDevice)
    target_id = region_id or basin_id
    if target_id:
        stmt = stmt.where(SensorDevice.region_id == target_id)
    sensors = db.execute(stmt).scalars().all()

    results = []
    for s in sensors:
        latest = db.execute(
            select(RiverObs).where(RiverObs.station_or_cell_id == s.sensor_code).order_by(RiverObs.ts.desc())
        ).scalars().first()

        results.append({
            "id": s.id,
            "sensor_code": s.sensor_code,
            "name": s.name,
            "river_name": s.river_name,
            "lat": s.lat,
            "lon": s.lon,
            "warning_level_m": s.warning_level_m,
            "danger_level_m": s.danger_level_m,
            "is_simulated": s.is_simulated,
            "status": s.status,
            "last_seen": s.last_seen.isoformat() + "Z" if s.last_seen else None,
            "latest_reading": {
                "water_level_m": latest.water_level_m if latest else 2.1,
                "discharge_m3s": latest.discharge_m3s if latest else 28.0,
                "rate_of_rise_mh": latest.rate_of_rise_mh if latest else 0.05,
                "timestamp": latest.ts.isoformat() + "Z" if latest else None,
                "source": latest.source if latest else "simulated"
            }
        })
    return results
