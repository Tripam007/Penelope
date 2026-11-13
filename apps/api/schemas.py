"""
PENELOPE Backend - Pydantic v2 Schemas
Strict typing for request/response payloads, IoT ingest, and GeoJSON outputs.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field, ConfigDict


# Base Config
class OrmBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# Sensor Ingest Schema (Hard Rule 3)
class SensorIngestRequest(BaseModel):
    sensor_code: str = Field(..., description="Unique alphanumeric sensor station identifier")
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)
    water_level_m: float = Field(..., ge=0.0, le=50.0, description="Current river stage gauge reading in meters")
    rate_of_rise_mh: Optional[float] = Field(0.0, description="Rate of change in meters per hour")
    discharge_rate_m3s: Optional[float] = Field(0.0, ge=0.0, description="Discharge in cubic meters per second")
    source: Literal["live", "simulated"] = Field("live", description="Data provenance: live or simulated")
    battery_level_pct: Optional[float] = Field(100.0, ge=0.0, le=100.0)


class SensorReadingResponse(OrmBase):
    id: str
    sensor_id: str
    timestamp: datetime
    water_level_m: float
    rate_of_rise_mh: float
    discharge_rate_m3s: float
    source: str


class SensorResponse(OrmBase):
    id: str
    basin_id: str
    sensor_code: str
    name: str
    river_name: str
    lat: float
    lon: float
    warning_level_m: float
    danger_level_m: float
    is_simulated: bool
    status: str
    latest_reading: Optional[SensorReadingResponse] = None


# Village & Shelter Schemas
class ShelterResponse(OrmBase):
    id: str
    basin_id: str
    name: str
    hindi_name: Optional[str] = None
    lat: float
    lon: float
    elevation_m: float
    capacity_persons: int
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None
    status: str


class VillageResponse(OrmBase):
    id: str
    basin_id: str
    name: str
    hindi_name: Optional[str] = None
    lat: float
    lon: float
    elevation_m: float
    slope_degrees: float
    population: int
    river_distance_m: float
    current_risk_score: float
    current_risk_level: str
    last_risk_update: datetime
    safe_shelter_id: Optional[str] = None
    safe_shelter: Optional[ShelterResponse] = None


# Basin Schema
class BasinResponse(OrmBase):
    id: str
    name: str
    hindi_name: Optional[str] = None
    state: str
    district: str
    center_lat: float
    center_lon: float


# Alert Schemas
class AlertDeliveryResponse(OrmBase):
    id: str
    channel: str
    recipient: str
    status: str  # pending, delivered, failed, skipped_unconfigured
    error_message: Optional[str] = None
    attempted_at: datetime


class AlertResponse(OrmBase):
    id: str
    village_id: Optional[str] = None
    basin_id: str
    severity: str
    title: str
    title_hi: Optional[str] = None
    message: str
    message_hi: Optional[str] = None
    risk_score: float
    triggered_at: datetime
    status: str
    deliveries: List[AlertDeliveryResponse] = []


class ManualAlertTriggerRequest(BaseModel):
    basin_id: str
    village_id: Optional[str] = None
    severity: Literal["Low", "Moderate", "High", "Very High"]
    title: str
    title_hi: Optional[str] = None
    message: str
    message_hi: Optional[str] = None
    channels: List[Literal["SMS", "Telegram", "Email", "Webhook", "Push"]] = ["SMS", "Telegram", "Email", "Webhook"]


# Map GeoJSON Feature Collection
class GeoJSONFeature(BaseModel):
    type: str = "Feature"
    geometry: Dict[str, Any]
    properties: Dict[str, Any]


class GeoJSONFeatureCollection(BaseModel):
    type: str = "FeatureCollection"
    features: List[GeoJSONFeature]


# Model Transparency & Metrics Schema (Hard Rule 4)
class ModelMetricsReport(BaseModel):
    model_name: str
    timestamp: str
    dataset_size: int
    metrics: Dict[str, Any]
    feature_importances: Dict[str, float]
    disclaimer: str

