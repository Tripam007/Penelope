"""
PENELOPE Backend - Database Seeding Script (Part 1 Specification)
Loads:
1. 3 Demo Hilly Regions (Uttarakhand-Chamoli, Himachal-Kullu, Kerala-Wayanad)
   with full PostGIS boundary MultiPolygon & Centroid geometries.
2. >= 200 real locations per region (villages, towns, tourist spots, treks, bridges, shelters).
3. Demo users for EVERY role (citizen, tourist, authority, responder, ngo, admin).
4. Sensor devices, grid cells, weather & river telemetry observations.
"""

import logging
from datetime import datetime, timedelta
from sqlalchemy import select, func
from apps.api.database import SessionLocal, init_db
from apps.api.models import (
    Region,
    Location,
    GridCell,
    User,
    SensorDevice,
    WeatherObs,
    RiverObs
)
from apps.api.geo_types import (
    make_point_geojson,
    make_multipolygon_geojson,
    make_polygon_geojson
)
from apps.api.auth.security import hash_password
from apps.api.ingestion.osm_seed_data import DEMO_REGIONS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("penelope.seed")

DEMO_USERS = [
    {
        "email": "citizen@penelope.org",
        "name": "Aarav Sharma",
        "role": "citizen",
        "org": "Chamoli Resident Union",
        "password": "Penelope@2026!"
    },
    {
        "email": "tourist@penelope.org",
        "name": "Elena Rostova",
        "role": "tourist",
        "org": "Himalayan Trekking Expedition",
        "password": "Penelope@2026!"
    },
    {
        "email": "authority@penelope.org",
        "name": "Dr. Rajeshwar Pant",
        "role": "authority",
        "org": "Uttarakhand State Disaster Management Authority",
        "password": "Penelope@2026!"
    },
    {
        "email": "responder@penelope.org",
        "name": "Commander Vikram Rathore",
        "role": "responder",
        "org": "NDRF 8th Battalion - Mountain Rescue",
        "password": "Penelope@2026!"
    },
    {
        "email": "ngo@penelope.org",
        "name": "Priyanka Nair",
        "role": "ngo",
        "org": "SEEDS Disaster Relief India",
        "password": "Penelope@2026!"
    },
    {
        "email": "admin@penelope.org",
        "name": "System Administrator",
        "role": "admin",
        "org": "PENELOPE Operations",
        "password": "Penelope@2026!"
    },
    {
        "email": "tripambiswas007@gmail.com",
        "name": "Tripam Biswas",
        "role": "admin",
        "org": "PENELOPE Disaster Management & Early Warning Directorate",
        "password": "Penelope@2026!"
    }
]


def seed_database():
    init_db()
    with SessionLocal() as db:
        # Always ensure all demo users exist and have correct roles
        for u_data in DEMO_USERS:
            existing_user = db.execute(select(User).where(User.email == u_data["email"])).scalar_one_or_none()
            if not existing_user:
                new_user = User(
                    email=u_data["email"],
                    password_hash=hash_password(u_data["password"]),
                    role=u_data["role"],
                    name=u_data["name"],
                    org=u_data["org"],
                    is_active=True
                )
                db.add(new_user)
            elif existing_user.email == "tripambiswas007@gmail.com":
                existing_user.role = "admin"
                existing_user.name = u_data["name"]
                existing_user.org = u_data["org"]
        db.commit()

        # Check if locations already seeded
        loc_count = db.execute(select(func.count(Location.id))).scalar() or 0
        user_count = db.execute(select(func.count(User.id))).scalar() or 0

        if loc_count >= 600 and user_count >= 7:
            logger.info(f"Database already seeded ({loc_count} locations, {user_count} users). Skipping duplicate geo seed.")
            return

        # 2. Seed Demo Regions & Locations
        for region_bundle in DEMO_REGIONS:
            r_info = region_bundle["region"]
            region = db.execute(select(Region).where(Region.name == r_info["name"])).scalar_one_or_none()
            if not region:
                c_lon, c_lat = r_info["centroid"]
                region = Region(
                    name=r_info["name"],
                    state=r_info["state"],
                    centroid=make_point_geojson(c_lon, c_lat),
                    geom=make_multipolygon_geojson(r_info["boundary"])
                )
                db.add(region)
                db.flush()

            # Seed Locations (>= 200 per region)
            existing_loc_names = {row[0] for row in db.execute(select(Location.name).where(Location.region_id == region.id)).fetchall()}
            for loc_info in region_bundle["locations"]:
                if loc_info["name"] in existing_loc_names:
                    continue
                location = Location(
                    region_id=region.id,
                    basin_id=region.id,
                    name=loc_info["name"],
                    hindi_name=loc_info.get("hindi_name"),
                    type=loc_info.get("type", "village"),
                    geom=make_point_geojson(loc_info["lon"], loc_info["lat"]),
                    elevation_m=loc_info.get("elevation_m", 1500.0),
                    population=loc_info.get("population", 500),
                    source="osm",
                    slope_degrees=loc_info.get("slope_degrees", 18.0),
                    river_distance_m=loc_info.get("river_distance_m", 250.0),
                    capacity_persons=loc_info.get("capacity_persons", 200),
                    status=loc_info.get("status", "Ready")
                )
                db.add(location)

            # Seed Terrain Grid Cells
            c_lon, c_lat = r_info["centroid"]
            cell_poly = [
                [
                    [c_lon - 0.02, c_lat - 0.02],
                    [c_lon + 0.02, c_lat - 0.02],
                    [c_lon + 0.02, c_lat + 0.02],
                    [c_lon - 0.02, c_lat + 0.02],
                    [c_lon - 0.02, c_lat - 0.02]
                ]
            ]
            cell = GridCell(
                region_id=region.id,
                geom=make_polygon_geojson(cell_poly),
                centroid=make_point_geojson(c_lon, c_lat),
                elevation_m=1650.0,
                slope_deg=22.0,
                aspect=175.0,
                twi=7.2,
                flow_accum=240.0,
                dist_to_river_m=120.0,
                landcover="forest",
                res_m=100.0
            )
            db.add(cell)
            db.flush()

            # Seed Sensors
            for s_info in region_bundle["sensors"]:
                existing_sensor = db.execute(select(SensorDevice).where(SensorDevice.name == s_info["name"])).scalar_one_or_none()
                if not existing_sensor:
                    sensor = SensorDevice(
                        id=s_info["sensor_code"],
                        sensor_code=s_info["sensor_code"],
                        name=s_info["name"],
                        geom=make_point_geojson(s_info["lon"], s_info["lat"]),
                        api_key_hash=hash_password("sim-sensor-key-2026"),
                        river_name=s_info["river_name"],
                        warning_level_m=s_info["warning_level_m"],
                        danger_level_m=s_info["danger_level_m"],
                        is_simulated=s_info.get("is_simulated", True),
                        region_id=region.id,
                        basin_id=region.id,
                        status="online"
                    )
                    db.add(sensor)

                    # Initial reading
                    obs = RiverObs(
                        station_or_cell_id=s_info["sensor_code"],
                        sensor_id=s_info["sensor_code"],
                        ts=datetime.utcnow(),
                        timestamp=datetime.utcnow(),
                        discharge_m3s=38.5,
                        discharge_rate_m3s=38.5,
                        level_m=2.2,
                        water_level_m=2.2,
                        rate_of_rise_mh=0.0,
                        source="simulated"
                    )
                    db.add(obs)

        db.commit()
        logger.info("PENELOPE Part 1 seeding completed successfully!")


if __name__ == "__main__":
    seed_database()
