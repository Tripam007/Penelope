"""
PENELOPE Backend - Simulated Sensor Generator (Hard Rule 3 Compliance)
Simulates realistic river-gauge IoT sensors.
Every generated reading is strictly labeled with source="simulated".
Never present simulated data as live.
"""

import math
import random
import logging
from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy import select
from sqlalchemy.orm import Session
from apps.api.models import Sensor, SensorReading

logger = logging.getLogger("penelope.ingestion.sensor_sim")


class SensorSimulatorDaemon:
    def __init__(self):
        self._step_counter = 0

    def generate_simulated_readings(self, db: Session) -> List[Dict[str, Any]]:
        """
        Generates realistic physical water-level telemetry for all simulated sensors.
        Simulates diurnal river baseflow + stochastic mountain runoff surges.
        """
        stmt = select(Sensor).where(Sensor.is_simulated.is_(True))
        result = db.execute(stmt)
        sim_sensors = result.scalars().all()

        if not sim_sensors:
            return []

        self._step_counter += 1
        now = datetime.utcnow()
        created_readings = []

        for sensor in sim_sensors:
            base_level = (sensor.warning_level_m * 0.45)
            diurnal_wave = 0.25 * math.sin(self._step_counter * 0.15 + (sensor.lat * 10))

            surge_cycle = (self._step_counter % 24)
            if 10 <= surge_cycle <= 15:
                surge = 1.2 + 0.8 * math.sin((surge_cycle - 10) * 0.6)
                rate_of_rise = 0.45 + random.uniform(0.05, 0.25)
            else:
                surge = random.uniform(-0.1, 0.1)
                rate_of_rise = random.uniform(-0.08, 0.08)

            water_level = max(0.5, round(base_level + diurnal_wave + surge, 2))
            discharge = max(5.0, round(water_level * 12.5 + random.uniform(0, 5), 1))

            reading = SensorReading(
                station_or_cell_id=sensor.sensor_code or sensor.id,
                sensor_id=sensor.id,
                ts=now,
                timestamp=now,
                level_m=water_level,
                water_level_m=water_level,
                rate_of_rise_mh=round(rate_of_rise, 3),
                discharge_m3s=discharge,
                discharge_rate_m3s=discharge,
                source="simulated"  # Strictly marked simulated per Hard Rule 3
            )
            db.add(reading)
            created_readings.append({
                "sensor_code": sensor.sensor_code,
                "sensor_name": sensor.name,
                "water_level_m": water_level,
                "rate_of_rise_mh": round(rate_of_rise, 3),
                "discharge_rate_m3s": discharge,
                "source": "simulated",
                "timestamp": now.isoformat()
            })

        db.commit()
        return created_readings
