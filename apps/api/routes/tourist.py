"""
PENELOPE Backend - Tourist Advisory & Plain-Language Safety Engine (Part 4)
Supplies actionable real-time and 24h/48h flash flood risk guidance for trekkers and pilgrims.
"""

from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from apps.api.database import get_db
from apps.api.models import Location, Region, WeatherObs
from apps.api.geo_types import extract_lon_lat
from apps.api.geospatial.risk_engine import haversine_km, rollup_location_risk
from apps.api.geospatial.routing import routing_engine

router = APIRouter(prefix="/tourist", tags=["Tourist Safety"])


ADVICE_TEMPLATES = {
    "Low": {
        "level": "NORMAL",
        "en": "Conditions are safe. Mountain passes, pilgrim routes, and river crossings are clear. Enjoy your trek, but stay tuned to evening rainfall forecasts.",
        "hi": "परिस्थितियां सामान्य और सुरक्षित हैं। पर्वतीय मार्ग और नदियां सुरक्षित हैं। अपनी यात्रा का आनंद लें, लेकिन शाम के मौसम के पूर्वानुमान पर नज़र रखें।"
    },
    "Moderate": {
        "level": "CAUTION",
        "en": "Caution advised. Intermittent rain and runoff detected in this catchment. Avoid setting up camps directly on riverbanks or dry riverbeds. Stay alert to rapid water level rises.",
        "hi": "सावधानी बरतें। इस जलग्रहण क्षेत्र में रुक-रुक कर बारिश और बहाव देखा जा रहा है। नदी के किनारों या सूखी नदी में शिविर न लगाएं। जलस्तर में अचानक वृद्धि के प्रति सतर्क रहें।"
    },
    "High": {
        "level": "WARNING",
        "en": "Warning: High flash-flood risk in this valley. Do not attempt river crossings or approach suspension bridges. Move to higher ground or proceed toward the nearest designated shelter.",
        "hi": "चेतावनी: इस घाटी में अचानक बाढ़ का अत्यधिक खतरा है। नदी पार करने या झूला पुलों के पास जाने का प्रयास न करें। ऊंचे स्थानों पर जाएं या निकटतम राहत शिविर की ओर बढ़ें।"
    },
    "Very High": {
        "level": "EVACUATE",
        "en": "CRITICAL EMERGENCY: Severe flash flood and cloudburst hazard imminent. Evacuate valley floors and river corridors immediately. Head directly to designated high-ground relief shelters.",
        "hi": "अति गंभीर आपातकाल: अचानक बाढ़ और बादल फटने का तत्काल खतरा। तुरंत नदी घाटी और निचले इलाकों को खाली करें। सीधे चिन्हित उच्च-भूमि राहत शिविरों की ओर जाएं।"
    }
}


@router.get("/advice")
def get_tourist_advice(
    lat: float = Query(..., description="Tourist GPS latitude"),
    lng: Optional[float] = Query(None, description="Tourist GPS longitude"),
    lon: Optional[float] = Query(None, description="Alternative tourist GPS longitude"),
    lang: str = Query("en", description="Language: en or hi"),
    db: Session = Depends(get_db)
):
    """
    Tourist safety advisory endpoint:
    Returns current + 24h/48h flood risk, plain-language advice, weather summary,
    and nearest safe shelter for any coordinate.
    """
    t_lon = lng if lng is not None else lon
    if t_lon is None:
        raise HTTPException(status_code=400, detail="Missing longitude parameter ('lng' or 'lon').")

    locations = db.execute(select(Location)).scalars().all()
    if not locations:
        raise HTTPException(status_code=404, detail="No locations found in database.")

    # Find closest location
    closest_loc = None
    min_dist_km = float("inf")
    for loc in locations:
        l_lon, l_lat = extract_lon_lat(loc.geom)
        d = haversine_km(lat, t_lon, l_lat, l_lon)
        if d < min_dist_km:
            min_dist_km = d
            closest_loc = loc

    # Compute risk roll-up
    rollup = rollup_location_risk(closest_loc, db, radius_km=6.0)

    risk_level = rollup["current_risk_level"]
    template = ADVICE_TEMPLATES.get(risk_level, ADVICE_TEMPLATES["Low"])
    plain_advice = template["hi"] if lang.lower().startswith("hi") else template["en"]

    # Nearest open shelter
    nearest_shelter = routing_engine._find_nearest_open_shelter(
        db, t_lon, lat, region_id=closest_loc.region_id
    )

    # Weather summary
    weather = db.execute(
        select(WeatherObs)
        .where(WeatherObs.location_id == closest_loc.id)
        .order_by(WeatherObs.ts.desc())
        .limit(1)
    ).scalar_one_or_none()

    rain_val = weather.rain_3h_mm if weather else 10.0
    temp_val = weather.temp_c if weather else 18.0

    return {
        "query_coordinates": {"lat": round(lat, 5), "lon": round(t_lon, 5)},
        "nearest_location": {
            "id": closest_loc.id,
            "name": closest_loc.name,
            "hindi_name": closest_loc.hindi_name,
            "type": closest_loc.type,
            "elevation_m": closest_loc.elevation_m,
            "distance_km": round(min_dist_km, 2)
        },
        "advisory_level": template["level"],
        "risk_now": {
            "score": rollup["current_risk_score"],
            "level": rollup["current_risk_level"]
        },
        "risk_24h": {
            "score": rollup["risk_24h"],
            "level": rollup["risk_24h_level"]
        },
        "risk_48h": {
            "score": rollup["risk_48h"],
            "level": rollup["risk_48h_level"]
        },
        "plain_language_advice": plain_advice,
        "key_drivers": rollup["drivers"],
        "weather_summary": {
            "current_rain_3h_mm": rain_val,
            "temperature_c": temp_val,
            "forecast_24h_rain_mm": round(rain_val * 2.8, 1)
        },
        "nearest_shelter": nearest_shelter,
        "emergency_contacts": {
            "national_disaster_helpline": "1070",
            "state_disaster_control_room": "1077",
            "police_emergency": "112",
            "ndrf_helpline": "+91-11-24363260"
        },
        "disclaimer": "Advisory only. Always follow official IMD/NDMA/SDRF emergency instructions."
    }
