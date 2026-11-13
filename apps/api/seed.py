"""
PENELOPE Backend - Database Seeding Script
Seeds real Himalayan and Western Ghats basins, villages, shelters, and sensors.
"""

import logging
from sqlalchemy import select
from apps.api.database import SessionLocal, init_db
from apps.api.models import Basin, Village, Shelter, Sensor, SensorReading
from apps.api.ingestion.osm import REAL_OSM_BASIN_SEEDS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("penelope.seed")


def seed_database():
    init_db()
    with SessionLocal() as db:
        # Check if already seeded
        res = db.execute(select(Basin))
        existing_basins = res.scalars().all()
        if existing_basins:
            logger.info("Database already seeded. Skipping initial seed.")
            return

        logger.info("Seeding basins, villages, shelters, and sensors...")
        for seed_data in REAL_OSM_BASIN_SEEDS:
            basin_info = seed_data["basin"]
            basin = Basin(
                name=basin_info["name"],
                hindi_name=basin_info.get("hindi_name"),
                state=basin_info["state"],
                district=basin_info["district"],
                center_lat=basin_info["center_lat"],
                center_lon=basin_info["center_lon"],
            )
            db.add(basin)
            db.flush()

            # Seed shelters first
            created_shelters = []
            for sh_info in seed_data["shelters"]:
                shelter = Shelter(
                    basin_id=basin.id,
                    name=sh_info["name"],
                    hindi_name=sh_info.get("hindi_name"),
                    lat=sh_info["lat"],
                    lon=sh_info["lon"],
                    elevation_m=sh_info["elevation_m"],
                    capacity_persons=sh_info["capacity_persons"],
                    contact_person=sh_info.get("contact_person"),
                    contact_phone=sh_info.get("contact_phone"),
                    status="Ready"
                )
                db.add(shelter)
                created_shelters.append(shelter)
            db.flush()

            # Seed villages with terrain attributes
            for v_info in seed_data["villages"]:
                suitable_shelter = None
                for sh in created_shelters:
                    if sh.elevation_m >= v_info["elevation_m"]:
                        suitable_shelter = sh
                        break
                if not suitable_shelter and created_shelters:
                    suitable_shelter = created_shelters[0]

                village = Village(
                    basin_id=basin.id,
                    name=v_info["name"],
                    hindi_name=v_info.get("hindi_name"),
                    lat=v_info["lat"],
                    lon=v_info["lon"],
                    elevation_m=v_info["elevation_m"],
                    slope_degrees=v_info["slope_degrees"],
                    population=v_info["population"],
                    river_distance_m=v_info["river_distance_m"],
                    current_risk_score=0.18,
                    current_risk_level="Low",
                    safe_shelter_id=suitable_shelter.id if suitable_shelter else None
                )
                db.add(village)

            # Seed IoT River-Gauge Sensors
            for s_info in seed_data["sensors"]:
                sensor = Sensor(
                    basin_id=basin.id,
                    sensor_code=s_info["sensor_code"],
                    name=s_info["name"],
                    river_name=s_info["river_name"],
                    lat=s_info["lat"],
                    lon=s_info["lon"],
                    warning_level_m=s_info["warning_level_m"],
                    danger_level_m=s_info["danger_level_m"],
                    is_simulated=s_info.get("is_simulated", True),
                    status="online"
                )
                db.add(sensor)
                db.flush()

                initial_reading = SensorReading(
                    sensor_id=sensor.id,
                    water_level_m=round(sensor.warning_level_m * 0.55, 2),
                    rate_of_rise_mh=0.02,
                    discharge_rate_m3s=18.5,
                    source="simulated" if sensor.is_simulated else "live"
                )
                db.add(initial_reading)

        db.commit()
        logger.info("Database seeding completed successfully!")


if __name__ == "__main__":
    seed_database()
