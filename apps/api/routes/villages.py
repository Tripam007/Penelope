"""
PENELOPE Backend - Village Risk & Evacuation Endpoints (Part 4 Enhanced)
Supplies village roll-ups, multi-horizon risk (current + 24h/48h), drivers, and evacuation shelters.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select

from apps.api.database import get_db
from apps.api.models import Village, Shelter, Alert
from apps.api.schemas import VillageResponse
from apps.api.geospatial.risk_engine import rollup_location_risk

router = APIRouter(prefix="/villages", tags=["Villages"])


@router.get("", response_model=List[VillageResponse])
def list_villages(
    basin_id: Optional[str] = None,
    risk_level: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    stmt = select(Village)
    if basin_id:
        stmt = stmt.where(Village.basin_id == basin_id)
    if risk_level:
        stmt = stmt.where(Village.current_risk_level == risk_level)
    if search:
        stmt = stmt.where(Village.name.ilike(f"%{search}%"))

    stmt = stmt.order_by(Village.current_risk_score.desc())
    villages = db.execute(stmt).scalars().all()
    return villages


@router.get("/{village_id}")
def get_village_detail(village_id: str, db: Session = Depends(get_db)):
    """
    Returns full village details with roll-up risk:
    current risk, 24h/48h forecasted risk with causal drivers,
    nearest safe shelter, and recent alerts.
    """
    village = db.execute(select(Village).where(Village.id == village_id)).scalars().first()
    if not village:
        # Check by name
        village = db.execute(select(Village).where(Village.name == village_id)).scalars().first()

    if not village:
        raise HTTPException(status_code=404, detail="Village not found")

    # Dynamic risk roll-up from surrounding cells
    rollup = rollup_location_risk(village, db, radius_km=5.0)

    safe_shelter = None
    if village.safe_shelter_id:
        safe_shelter = db.execute(select(Shelter).where(Shelter.id == village.safe_shelter_id)).scalars().first()

    recent_alerts = db.execute(
        select(Alert)
        .where(Alert.village_id == village.id)
        .order_by(Alert.triggered_at.desc())
        .limit(5)
    ).scalars().all()

    return {
        "id": village.id,
        "basin_id": village.basin_id,
        "region_id": village.region_id,
        "name": village.name,
        "hindi_name": village.hindi_name,
        "lat": village.lat,
        "lon": village.lon,
        "elevation_m": village.elevation_m,
        "slope_degrees": village.slope_degrees,
        "population": village.population,
        "river_distance_m": village.river_distance_m,
        "current_risk_score": rollup["current_risk_score"],
        "current_risk_level": rollup["current_risk_level"],
        "risk_24h": rollup["risk_24h"],
        "risk_24h_level": rollup["risk_24h_level"],
        "risk_48h": rollup["risk_48h"],
        "risk_48h_level": rollup["risk_48h_level"],
        "drivers": rollup["drivers"],
        "cells_in_radius": rollup.get("cells_in_radius_count", 0),
        "last_risk_update": village.last_risk_update.isoformat() + "Z",
        "safe_shelter": {
            "id": safe_shelter.id,
            "name": safe_shelter.name,
            "hindi_name": safe_shelter.hindi_name,
            "elevation_m": safe_shelter.elevation_m,
            "capacity": safe_shelter.capacity_persons,
            "contact_person": safe_shelter.contact_person,
            "contact_phone": safe_shelter.contact_phone,
            "status": safe_shelter.status,
            "elevation_gain_m": round(safe_shelter.elevation_m - village.elevation_m, 1)
        } if safe_shelter else None,
        "recent_alerts": [
            {
                "id": a.id,
                "severity": a.severity,
                "title": a.title,
                "message": a.message,
                "triggered_at": a.triggered_at.isoformat() + "Z",
                "status": a.status
            }
            for a in recent_alerts
        ]
    }
