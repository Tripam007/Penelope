"""
PENELOPE Backend - MapLibre GeoJSON Endpoint
Supplies live 4-tier flash flood risk layers, sensor gauges, and evacuation paths.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from apps.api.database import get_db
from apps.api.models import Village, Sensor, Shelter, SensorReading, Basin

router = APIRouter(prefix="/map", tags=["Map"])


@router.get("/geojson")
def get_map_geojson_layers(db: Session = Depends(get_db)):
    """
    Returns unified GeoJSON FeatureCollection for MapLibre GL JS.
    """
    features = []

    # 1. Villages with Risk Levels
    villages = db.execute(select(Village)).scalars().all()
    for v in villages:
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [v.lon, v.lat]
            },
            "properties": {
                "layer_type": "village",
                "id": v.id,
                "name": v.name,
                "hindi_name": v.hindi_name,
                "risk_score": v.current_risk_score,
                "risk_level": v.current_risk_level,  # Low, Moderate, High, Very High
                "population": v.population,
                "elevation_m": v.elevation_m,
                "slope_degrees": v.slope_degrees,
                "river_distance_m": v.river_distance_m,
                "safe_shelter_id": v.safe_shelter_id,
            }
        })

    # 2. Sensors with Real-Time Water Levels & SIM Badges
    sensors = db.execute(select(Sensor)).scalars().all()
    for s in sensors:
        latest_reading = (
            db.execute(
                select(SensorReading)
                .where(SensorReading.sensor_id == s.id)
                .order_by(SensorReading.timestamp.desc())
                .limit(1)
            )
            .scalars()
            .first()
        )
        water_level = latest_reading.water_level_m if latest_reading else 1.5
        reading_source = latest_reading.source if latest_reading else ("simulated" if s.is_simulated else "live")
        danger_ratio = round(water_level / max(s.danger_level_m, 0.1), 2)

        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [s.lon, s.lat]
            },
            "properties": {
                "layer_type": "sensor",
                "id": s.id,
                "sensor_code": s.sensor_code,
                "name": s.name,
                "river_name": s.river_name,
                "water_level_m": water_level,
                "warning_level_m": s.warning_level_m,
                "danger_level_m": s.danger_level_m,
                "danger_ratio": danger_ratio,
                "is_simulated": s.is_simulated,
                "source": reading_source,  # "simulated" triggers "SIM" badge in UI
                "status": s.status,
            }
        })

    # 3. Safe Relief Shelters
    shelters = db.execute(select(Shelter)).scalars().all()
    shelter_map = {}
    for sh in shelters:
        shelter_map[sh.id] = sh
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [sh.lon, sh.lat]
            },
            "properties": {
                "layer_type": "shelter",
                "id": sh.id,
                "name": sh.name,
                "hindi_name": sh.hindi_name,
                "capacity": sh.capacity_persons,
                "elevation_m": sh.elevation_m,
                "contact_person": sh.contact_person,
                "contact_phone": sh.contact_phone,
                "status": sh.status,
            }
        })

    # 4. Evacuation Routes connecting villages to safe shelters
    for v in villages:
        if v.safe_shelter_id and v.safe_shelter_id in shelter_map:
            sh = shelter_map[v.safe_shelter_id]
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [v.lon, v.lat],
                        [sh.lon, sh.lat]
                    ]
                },
                "properties": {
                    "layer_type": "evacuation_route",
                    "village_id": v.id,
                    "village_name": v.name,
                    "shelter_name": sh.name,
                    "risk_level": v.current_risk_level,
                    "elev_gain_m": round(sh.elevation_m - v.elevation_m, 1)
                }
            })

    return {
        "type": "FeatureCollection",
        "features": features
    }
