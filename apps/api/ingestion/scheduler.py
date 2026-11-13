"""
PENELOPE Backend - APScheduler Ingestion & Risk Intelligence Jobs
Automates sensor simulation, Open-Meteo weather sync, and real-time ML risk re-evaluation.
"""

import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select

from apps.api.config import settings
from apps.api.database import SessionLocal
from apps.api.models import Basin, Village, Sensor, WeatherReading, Alert
from apps.api.ingestion.open_meteo import OpenMeteoClient
from apps.api.ingestion.sensor_sim import SensorSimulatorDaemon
from apps.api.alerts.dispatcher import alert_dispatcher
from ml.predictor import FloodRiskPredictor

logger = logging.getLogger("penelope.scheduler")

scheduler = AsyncIOScheduler()
open_meteo_client = OpenMeteoClient()
sensor_sim_daemon = SensorSimulatorDaemon()
ml_predictor = FloodRiskPredictor(model_dir=settings.MODEL_DIR)

# In-memory event buffer for WebSocket broadcasting
latest_broadcast_events = []


async def run_sensor_simulation_cycle():
    if not settings.SIMULATE_SENSORS:
        return

    with SessionLocal() as db:
        try:
            readings = sensor_sim_daemon.generate_simulated_readings(db)
            if readings:
                logger.info(f"Generated {len(readings)} simulated sensor readings.")
                latest_broadcast_events.append({
                    "type": "SENSOR_TELEMETRY",
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "data": readings
                })
        except Exception as e:
            logger.error(f"Error in sensor simulation cycle: {e}")


async def run_weather_and_risk_evaluation_cycle():
    with SessionLocal() as db:
        try:
            basins_stmt = select(Basin)
            res = db.execute(basins_stmt)
            basins = res.scalars().all()

            for basin in basins:
                weather = await open_meteo_client.fetch_weather_and_soil(basin.center_lat, basin.center_lon)
                flood = await open_meteo_client.fetch_glofas_river_discharge(basin.center_lat, basin.center_lon)

                snapshot = WeatherReading(
                    basin_id=basin.id,
                    timestamp=datetime.utcnow(),
                    lat=basin.center_lat,
                    lon=basin.center_lon,
                    rain_1h_mm=weather["rain_1h_mm"],
                    rain_3h_mm=weather["rain_3h_mm"],
                    rain_6h_mm=weather["rain_6h_mm"],
                    rain_24h_mm=weather["rain_24h_mm"],
                    soil_moisture_surface=weather["soil_moisture_0_to_1cm"],
                    soil_moisture_deep=weather["soil_moisture_9_to_27cm"],
                    glofas_discharge_m3s=flood["river_discharge_m3s"],
                    antecedent_precip_index=weather["rain_24h_mm"] * 0.85
                )
                db.add(snapshot)

                sensor_stmt = select(Sensor).where(Sensor.basin_id == basin.id)
                sensor_res = db.execute(sensor_stmt)
                sensors = sensor_res.scalars().all()
                sensor_level = 2.0
                danger_mark = 5.0
                if sensors:
                    sensor_level = sensors[0].warning_level_m * 0.7
                    danger_mark = sensors[0].danger_level_m

                village_stmt = select(Village).where(Village.basin_id == basin.id)
                v_res = db.execute(village_stmt)
                villages = v_res.scalars().all()

                for village in villages:
                    telemetry = {
                        "rain_1h_mm": weather["rain_1h_mm"],
                        "rain_3h_mm": weather["rain_3h_mm"],
                        "rain_6h_mm": weather["rain_6h_mm"],
                        "rain_24h_mm": weather["rain_24h_mm"],
                        "soil_moisture_0_to_1cm": weather["soil_moisture_0_to_1cm"],
                        "soil_moisture_9_to_27cm": weather["soil_moisture_9_to_27cm"],
                        "elevation_m": village.elevation_m,
                        "slope_degrees": village.slope_degrees,
                        "river_discharge_m3s": flood["river_discharge_m3s"],
                        "discharge_percentile_anomaly": flood["discharge_percentile_anomaly"],
                        "sensor_level_m": sensor_level,
                        "sensor_danger_mark_m": danger_mark,
                    }

                    risk_output = ml_predictor.predict_risk(telemetry)
                    prev_level = village.current_risk_level
                    village.current_risk_score = risk_output["risk_score"]
                    village.current_risk_level = risk_output["risk_level"]
                    village.last_risk_update = datetime.utcnow()

                    if village.current_risk_level in ["High", "Very High"] and prev_level not in ["High", "Very High"]:
                        alert = Alert(
                            village_id=village.id,
                            basin_id=basin.id,
                            severity=village.current_risk_level,
                            title=f"Flash Flood {village.current_risk_level} Advisory for {village.name}",
                            title_hi=f"{village.hindi_name or village.name} के लिए अचानक बाढ़ चेतावनी",
                            message=f"Critical rainfall rate and river runoff surge detected. Predicted 3h flood risk: {int(risk_output['risk_score']*100)}%. Proceed to designated safe relief shelters.",
                            message_hi="अत्यधिक वर्षा और जलस्तर में वृद्धि। तत्काल सुरक्षित राहत शिविरों की ओर प्रस्थान करें।",
                            risk_score=risk_output["risk_score"],
                            triggered_at=datetime.utcnow(),
                            status="Active"
                        )
                        db.add(alert)
                        db.flush()
                        alert_dispatcher.dispatch_alert(db, alert)

                        latest_broadcast_events.append({
                            "type": "ALERT_TRIGGERED",
                            "timestamp": datetime.utcnow().isoformat() + "Z",
                            "data": {
                                "village_id": village.id,
                                "village_name": village.name,
                                "severity": village.current_risk_level,
                                "risk_score": risk_output["risk_score"]
                            }
                        })

            db.commit()
            logger.info("Weather sync and village ML risk re-evaluation completed.")
        except Exception as e:
            logger.error(f"Error in weather/risk evaluation cycle: {e}")


def start_scheduler():
    scheduler.add_job(
        run_sensor_simulation_cycle,
        "interval",
        seconds=settings.SIMULATION_INTERVAL_SECONDS,
        id="sensor_sim_job",
        replace_existing=True
    )
    scheduler.add_job(
        run_weather_and_risk_evaluation_cycle,
        "interval",
        minutes=5,
        id="weather_risk_job",
        replace_existing=True
    )
    scheduler.start()
    logger.info("APScheduler background ingestion service started.")


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()
        logger.info("APScheduler stopped.")
