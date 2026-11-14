"""
PENELOPE Backend - SQLAlchemy 2.0 Declarative Database Models
Defines complete PostGIS schema for Part 1:
- regions (basins/catchments)
- locations (villages, towns, tourist spots, treks, bridges, shelters)
- grid_cells (hydrology & DEM terrain grid cells)
- weather_obs (meteorological time-series)
- river_obs (hydrological river discharge & water levels)
- predictions (AI multi-horizon flood probabilities & drivers)
- alerts (multi-lingual flood warning dispatches)
- alert_deliveries (multi-channel delivery logs)
- subscriptions (citizen/responder alert subscriptions)
- users (RBAC authentication & user management)
- sensor_devices (IoT river gauge registration & telemetry)
"""

import uuid
from datetime import datetime
from typing import List, Optional, Any, Dict
from sqlalchemy import (
    String,
    Float,
    Integer,
    Boolean,
    DateTime,
    ForeignKey,
    Text,
    Index,
    JSON,
    UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from apps.api.database import Base
from apps.api.geo_types import PointGeometry, PolygonGeometry, MultiPolygonGeometry, extract_lon_lat


def generate_uuid() -> str:
    return str(uuid.uuid4())


# ============================================================================
# 1. REGIONS (Basins / Mountain Catchments)
# ============================================================================
class Region(Base):
    __tablename__ = "regions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    state: Mapped[str] = mapped_column(String(60), index=True)
    geom: Mapped[Optional[Any]] = mapped_column(MultiPolygonGeometry(srid=4326), nullable=True)
    centroid: Mapped[Optional[Any]] = mapped_column(PointGeometry(srid=4326), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Compatibility attributes
    hindi_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Relationships
    locations: Mapped[List["Location"]] = relationship("Location", back_populates="region", cascade="all, delete-orphan")
    grid_cells: Mapped[List["GridCell"]] = relationship("GridCell", back_populates="region", cascade="all, delete-orphan")
    alerts: Mapped[List["Alert"]] = relationship("Alert", back_populates="region", cascade="all, delete-orphan")
    users: Mapped[List["User"]] = relationship("User", back_populates="region")

    @property
    def district(self) -> str:
        return self.name.split("(")[-1].replace(")", "").strip() if "(" in self.name else self.name

    @property
    def center_lat(self) -> float:
        _, lat = extract_lon_lat(self.centroid)
        return lat

    @property
    def center_lon(self) -> float:
        lon, _ = extract_lon_lat(self.centroid)
        return lon


# Backward-compatible alias for existing endpoints
Basin = Region


# ============================================================================
# 2. LOCATIONS (Villages, Towns, Tourist Spots, Treks, Bridges, Shelters)
# ============================================================================
class Location(Base):
    __tablename__ = "locations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    region_id: Mapped[str] = mapped_column(String(36), ForeignKey("regions.id"), index=True)
    basin_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(140), index=True)
    type: Mapped[str] = mapped_column(String(40), index=True, default="village")  # village, town, tourist_spot, trek, bridge, shelter
    geom: Mapped[Any] = mapped_column(PointGeometry(srid=4326), nullable=False)
    elevation_m: Mapped[float] = mapped_column(Float, default=1500.0)
    population: Mapped[int] = mapped_column(Integer, default=500)
    source: Mapped[str] = mapped_column(String(60), default="osm")  # osm, survey_of_india, simulated
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Optional metadata / links
    hindi_name: Mapped[Optional[str]] = mapped_column(String(140), nullable=True)
    current_risk_score: Mapped[float] = mapped_column(Float, default=0.15)
    current_risk_level: Mapped[str] = mapped_column(String(20), default="Low")
    last_risk_update: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    slope_degrees: Mapped[float] = mapped_column(Float, default=18.0)
    river_distance_m: Mapped[float] = mapped_column(Float, default=250.0)
    safe_shelter_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    capacity_persons: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, default=200)
    contact_person: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    contact_phone: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="Ready")

    # Relationships
    region: Mapped["Region"] = relationship("Region", back_populates="locations")
    weather_obs: Mapped[List["WeatherObs"]] = relationship("WeatherObs", back_populates="location", cascade="all, delete-orphan")

    @property
    def basin(self) -> "Region":
        return self.region

    @property
    def safe_shelter(self) -> Optional["Location"]:
        return None

    @property
    def lat(self) -> float:
        _, lat = extract_lon_lat(self.geom)
        return lat

    @property
    def lon(self) -> float:
        lon, _ = extract_lon_lat(self.geom)
        return lon


# Backward-compatible aliases for legacy routes
Village = Location
Shelter = Location


# ============================================================================
# 3. GRID CELLS (Topography, Flow Accumulation, TWI, DEM)
# ============================================================================
class GridCell(Base):
    __tablename__ = "grid_cells"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    region_id: Mapped[str] = mapped_column(String(36), ForeignKey("regions.id"), index=True)
    geom: Mapped[Any] = mapped_column(PolygonGeometry(srid=4326), nullable=False)
    centroid: Mapped[Any] = mapped_column(PointGeometry(srid=4326), nullable=False)
    elevation_m: Mapped[float] = mapped_column(Float, default=1200.0)
    slope_deg: Mapped[float] = mapped_column(Float, default=15.0)
    aspect: Mapped[float] = mapped_column(Float, default=180.0)
    twi: Mapped[float] = mapped_column(Float, default=6.5)  # Topographic Wetness Index
    flow_accum: Mapped[float] = mapped_column(Float, default=120.0)
    dist_to_river_m: Mapped[float] = mapped_column(Float, default=200.0)
    landcover: Mapped[str] = mapped_column(String(60), default="forest")
    res_m: Mapped[float] = mapped_column(Float, default=100.0)  # Resolution in meters

    # Relationships
    region: Mapped["Region"] = relationship("Region", back_populates="grid_cells")
    weather_obs: Mapped[List["WeatherObs"]] = relationship("WeatherObs", back_populates="cell", cascade="all, delete-orphan")
    predictions: Mapped[List["Prediction"]] = relationship("Prediction", back_populates="cell", cascade="all, delete-orphan")


# ============================================================================
# 4. WEATHER OBSERVATIONS
# ============================================================================
class WeatherObs(Base):
    __tablename__ = "weather_obs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    cell_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("grid_cells.id"), nullable=True, index=True)
    location_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("locations.id"), nullable=True, index=True)
    basin_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    ts: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    timestamp: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    precip_mm: Mapped[float] = mapped_column(Float, default=0.0)
    rain_1h_mm: Mapped[float] = mapped_column(Float, default=0.0)
    rain_3h_mm: Mapped[float] = mapped_column(Float, default=0.0)
    rain_6h_mm: Mapped[float] = mapped_column(Float, default=0.0)
    rain_24h_mm: Mapped[float] = mapped_column(Float, default=0.0)
    temp_c: Mapped[float] = mapped_column(Float, default=20.0)
    humidity: Mapped[float] = mapped_column(Float, default=70.0)
    soil_moisture: Mapped[float] = mapped_column(Float, default=0.28)
    soil_moisture_surface: Mapped[float] = mapped_column(Float, default=0.25)
    soil_moisture_deep: Mapped[float] = mapped_column(Float, default=0.30)
    pressure: Mapped[float] = mapped_column(Float, default=1013.25)
    wind: Mapped[float] = mapped_column(Float, default=5.0)
    glofas_discharge_m3s: Mapped[float] = mapped_column(Float, default=15.0)
    antecedent_precip_index: Mapped[float] = mapped_column(Float, default=0.0)
    source: Mapped[str] = mapped_column(String(60), default="open_meteo")

    # Relationships
    cell: Mapped[Optional["GridCell"]] = relationship("GridCell", back_populates="weather_obs")
    location: Mapped[Optional["Location"]] = relationship("Location", back_populates="weather_obs")

    __table_args__ = (
        UniqueConstraint("cell_id", "ts", "source", name="uq_weather_obs_cell_ts_source"),
    )


# Backward-compatible alias
WeatherReading = WeatherObs


# ============================================================================
# 5. RIVER OBSERVATIONS (Hydrology & Gauges)
# ============================================================================
class RiverObs(Base):
    __tablename__ = "river_obs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    station_or_cell_id: Mapped[str] = mapped_column(String(60), index=True, default="")
    sensor_id: Mapped[Optional[str]] = mapped_column(String(60), index=True, nullable=True)
    ts: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    timestamp: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    discharge_m3s: Mapped[float] = mapped_column(Float, default=0.0)
    discharge_rate_m3s: Mapped[float] = mapped_column(Float, default=0.0)
    level_m: Mapped[float] = mapped_column(Float, default=0.0)
    water_level_m: Mapped[float] = mapped_column(Float, default=0.0)
    rate_of_rise_mh: Mapped[float] = mapped_column(Float, default=0.0)
    source: Mapped[str] = mapped_column(String(30), default="sensor")


# Backward-compatible alias
SensorReading = RiverObs


# ============================================================================
# 6. PREDICTIONS (AI Multi-Horizon Outputs)
# ============================================================================
class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    cell_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("grid_cells.id"), nullable=True, index=True)
    location_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("locations.id"), nullable=True, index=True)
    issued_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    horizon_h: Mapped[int] = mapped_column(Integer, default=1)  # 1h, 3h, 6h, 24h
    prob: Mapped[float] = mapped_column(Float, default=0.0)  # 0.0 - 1.0
    severity: Mapped[str] = mapped_column(String(30), default="low")  # low, moderate, high, very_high
    drivers: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)  # contributing feature importances
    model_version: Mapped[str] = mapped_column(String(60), default="lightgbm-v1.0")

    # Relationships
    cell: Mapped[Optional["GridCell"]] = relationship("GridCell", back_populates="predictions")


# ============================================================================
# 7. ALERTS (Early Warning Dispatches)
# ============================================================================
class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    region_id: Mapped[str] = mapped_column(String(36), ForeignKey("regions.id"), index=True)
    basin_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    cell_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("grid_cells.id"), nullable=True)
    location_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("locations.id"), nullable=True, index=True)
    village_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    severity: Mapped[str] = mapped_column(String(30), index=True)  # low, moderate, high, very_high
    message_i18n: Mapped[Dict[str, str]] = mapped_column(JSON, default=dict)  # {"en": "...", "hi": "..."}
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    triggered_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="active", index=True)  # active, resolved, expired
    issued_by: Mapped[str] = mapped_column(String(120), default="system")

    title: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    title_hi: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    message_hi: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    risk_score: Mapped[float] = mapped_column(Float, default=0.5)

    # Relationships
    region: Mapped["Region"] = relationship("Region", back_populates="alerts")
    deliveries: Mapped[List["AlertDelivery"]] = relationship("AlertDelivery", back_populates="alert", cascade="all, delete-orphan")


# ============================================================================
# 8. ALERT DELIVERIES
# ============================================================================
class AlertDelivery(Base):
    __tablename__ = "alert_deliveries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    alert_id: Mapped[str] = mapped_column(String(36), ForeignKey("alerts.id"), index=True)
    subscription_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("subscriptions.id"), nullable=True, index=True)
    channel: Mapped[str] = mapped_column(String(30))  # sms, push, telegram, email, webhook
    status: Mapped[str] = mapped_column(String(40))  # pending, delivered, failed, skipped_unconfigured
    provider_msg_id: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    recipient: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ts: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    attempted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    alert: Mapped["Alert"] = relationship("Alert", back_populates="deliveries")


# ============================================================================
# 9. SUBSCRIPTIONS
# ============================================================================
class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    channel: Mapped[str] = mapped_column(String(30))  # sms, push, telegram, email, webhook
    target: Mapped[str] = mapped_column(String(255))  # phone, push-token, chat-id, email, url
    locations: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)  # geom + radius_km
    min_severity: Mapped[str] = mapped_column(String(30), default="high")  # low, moderate, high, very_high
    language: Mapped[str] = mapped_column(String(10), default="en")  # en, hi
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="subscriptions")


# ============================================================================
# 10. USERS (RBAC Authentication)
# ============================================================================
class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    email: Mapped[str] = mapped_column(String(160), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(40), index=True, default="citizen")  # citizen, tourist, authority, responder, ngo, admin
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    org: Mapped[Optional[str]] = mapped_column(String(160), nullable=True)
    region_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("regions.id"), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    region: Mapped[Optional["Region"]] = relationship("Region", back_populates="users")
    subscriptions: Mapped[List["Subscription"]] = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")


# ============================================================================
# 11. SENSOR DEVICES
# ============================================================================
class SensorDevice(Base):
    __tablename__ = "sensor_devices"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    sensor_code: Mapped[str] = mapped_column(String(60), index=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(120), index=True)
    geom: Mapped[Any] = mapped_column(PointGeometry(srid=4326), nullable=False)
    api_key_hash: Mapped[str] = mapped_column(String(128), index=True, default="default-hash")
    last_seen: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    river_name: Mapped[str] = mapped_column(String(80), default="Alaknanda")
    warning_level_m: Mapped[float] = mapped_column(Float, default=3.5)
    danger_level_m: Mapped[float] = mapped_column(Float, default=5.0)
    is_simulated: Mapped[bool] = mapped_column(Boolean, default=False)
    region_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("regions.id"), nullable=True)
    basin_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="online")

    @property
    def lat(self) -> float:
        _, lat = extract_lon_lat(self.geom)
        return lat

    @property
    def lon(self) -> float:
        lon, _ = extract_lon_lat(self.geom)
        return lon


# Backward-compatible alias
Sensor = SensorDevice
