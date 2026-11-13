"""
PENELOPE Backend - SQLAlchemy 2.0 Declarative Database Models
"""

import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import (
    String,
    Float,
    Integer,
    Boolean,
    DateTime,
    ForeignKey,
    Text,
    Index
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from apps.api.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class Basin(Base):
    __tablename__ = "basins"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    hindi_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    state: Mapped[str] = mapped_column(String(60))
    district: Mapped[str] = mapped_column(String(60))
    center_lat: Mapped[float] = mapped_column(Float)
    center_lon: Mapped[float] = mapped_column(Float)
    boundary_geojson: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    villages: Mapped[List["Village"]] = relationship("Village", back_populates="basin", cascade="all, delete-orphan")
    sensors: Mapped[List["Sensor"]] = relationship("Sensor", back_populates="basin", cascade="all, delete-orphan")
    shelters: Mapped[List["Shelter"]] = relationship("Shelter", back_populates="basin", cascade="all, delete-orphan")


class Shelter(Base):
    __tablename__ = "shelters"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    basin_id: Mapped[str] = mapped_column(String(36), ForeignKey("basins.id"), index=True)
    name: Mapped[str] = mapped_column(String(120), index=True)
    hindi_name: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    lat: Mapped[float] = mapped_column(Float)
    lon: Mapped[float] = mapped_column(Float)
    elevation_m: Mapped[float] = mapped_column(Float)
    capacity_persons: Mapped[int] = mapped_column(Integer, default=200)
    contact_person: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    contact_phone: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="Ready")  # Ready, Active, Full
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    basin: Mapped["Basin"] = relationship("Basin", back_populates="shelters")


class Village(Base):
    __tablename__ = "villages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    basin_id: Mapped[str] = mapped_column(String(36), ForeignKey("basins.id"), index=True)
    name: Mapped[str] = mapped_column(String(120), index=True)
    hindi_name: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    lat: Mapped[float] = mapped_column(Float)
    lon: Mapped[float] = mapped_column(Float)
    elevation_m: Mapped[float] = mapped_column(Float)
    slope_degrees: Mapped[float] = mapped_column(Float, default=18.0)
    population: Mapped[int] = mapped_column(Integer, default=500)
    river_distance_m: Mapped[float] = mapped_column(Float, default=250.0)

    current_risk_score: Mapped[float] = mapped_column(Float, default=0.15)
    current_risk_level: Mapped[str] = mapped_column(String(20), default="Low")  # Low, Moderate, High, Very High
    last_risk_update: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    safe_shelter_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("shelters.id"), nullable=True)

    basin: Mapped["Basin"] = relationship("Basin", back_populates="villages")
    safe_shelter: Mapped[Optional["Shelter"]] = relationship("Shelter")
    alerts: Mapped[List["Alert"]] = relationship("Alert", back_populates="village")


class Sensor(Base):
    __tablename__ = "sensors"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    basin_id: Mapped[str] = mapped_column(String(36), ForeignKey("basins.id"), index=True)
    sensor_code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    river_name: Mapped[str] = mapped_column(String(80))
    lat: Mapped[float] = mapped_column(Float)
    lon: Mapped[float] = mapped_column(Float)
    warning_level_m: Mapped[float] = mapped_column(Float, default=3.5)
    danger_level_m: Mapped[float] = mapped_column(Float, default=5.0)
    is_simulated: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(String(20), default="online")  # online, offline
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    basin: Mapped["Basin"] = relationship("Basin", back_populates="sensors")
    readings: Mapped[List["SensorReading"]] = relationship("SensorReading", back_populates="sensor", cascade="all, delete-orphan")


class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    sensor_id: Mapped[str] = mapped_column(String(36), ForeignKey("sensors.id"), index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    water_level_m: Mapped[float] = mapped_column(Float)
    rate_of_rise_mh: Mapped[float] = mapped_column(Float, default=0.0)
    discharge_rate_m3s: Mapped[float] = mapped_column(Float, default=0.0)
    source: Mapped[str] = mapped_column(String(20), default="live")  # "live" or "simulated"

    sensor: Mapped["Sensor"] = relationship("Sensor", back_populates="readings")

    __table_args__ = (
        Index("idx_sensor_readings_sensor_time", "sensor_id", "timestamp"),
    )


class WeatherReading(Base):
    __tablename__ = "weather_readings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    basin_id: Mapped[str] = mapped_column(String(36), ForeignKey("basins.id"), index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    lat: Mapped[float] = mapped_column(Float)
    lon: Mapped[float] = mapped_column(Float)
    rain_1h_mm: Mapped[float] = mapped_column(Float, default=0.0)
    rain_3h_mm: Mapped[float] = mapped_column(Float, default=0.0)
    rain_6h_mm: Mapped[float] = mapped_column(Float, default=0.0)
    rain_24h_mm: Mapped[float] = mapped_column(Float, default=0.0)
    soil_moisture_surface: Mapped[float] = mapped_column(Float, default=0.25)
    soil_moisture_deep: Mapped[float] = mapped_column(Float, default=0.30)
    glofas_discharge_m3s: Mapped[float] = mapped_column(Float, default=15.0)
    antecedent_precip_index: Mapped[float] = mapped_column(Float, default=0.0)


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    village_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("villages.id"), nullable=True, index=True)
    basin_id: Mapped[str] = mapped_column(String(36), ForeignKey("basins.id"), index=True)
    severity: Mapped[str] = mapped_column(String(20))  # Low, Moderate, High, Very High
    title: Mapped[str] = mapped_column(String(150))
    title_hi: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    message: Mapped[str] = mapped_column(Text)
    message_hi: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    risk_score: Mapped[float] = mapped_column(Float)
    triggered_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    status: Mapped[str] = mapped_column(String(20), default="Active")  # Active, Resolved

    village: Mapped[Optional["Village"]] = relationship("Village", back_populates="alerts")
    deliveries: Mapped[List["AlertDelivery"]] = relationship("AlertDelivery", back_populates="alert", cascade="all, delete-orphan")


class AlertDelivery(Base):
    __tablename__ = "alert_deliveries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    alert_id: Mapped[str] = mapped_column(String(36), ForeignKey("alerts.id"), index=True)
    channel: Mapped[str] = mapped_column(String(30))  # SMS, Telegram, Email, Webhook, Push
    recipient: Mapped[str] = mapped_column(String(120))
    status: Mapped[str] = mapped_column(String(30))  # pending, delivered, failed, skipped_unconfigured
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    attempted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    alert: Mapped["Alert"] = relationship("Alert", back_populates="deliveries")
