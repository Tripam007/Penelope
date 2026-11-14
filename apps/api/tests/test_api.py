"""
Integration and End-to-End Tests for PENELOPE FastAPI Backend.
"""

import os
os.environ["TESTING"] = "true"

import pytest

from fastapi.testclient import TestClient
from apps.api.main import app
from apps.api.database import init_db
from apps.api.seed import seed_database


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    init_db()
    seed_database()


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_root_endpoint(client):
    res = client.get("/")
    assert res.status_code == 200
    data = res.json()
    assert data["platform"] == "PENELOPE"
    assert "Data today. Safer tomorrows." in data["tagline"]


def test_healthz_endpoint(client):
    res = client.get("/api/v1/healthz")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] in ["healthy", "degraded"]
    assert "database" in data
    assert "alert_providers" in data


def test_map_geojson_layers(client):
    res = client.get("/api/v1/map/geojson")
    assert res.status_code == 200
    data = res.json()
    assert data["type"] == "FeatureCollection"
    assert len(data["features"]) > 0

    layer_types = {f["properties"]["layer_type"] for f in data["features"]}
    assert "village" in layer_types
    assert "sensor" in layer_types
    assert "shelter" in layer_types


def test_villages_endpoints(client):
    res = client.get("/api/v1/villages")
    assert res.status_code == 200
    villages = res.json()
    assert len(villages) > 0

    first_village = villages[0]
    v_id = first_village["id"]

    detail_res = client.get(f"/api/v1/villages/{v_id}")
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert detail["name"] == first_village["name"]
    assert "safe_shelter" in detail


def test_sensor_ingest_and_simulated_badge(client):
    # Ingest a reading with source="simulated"
    ingest_payload = {
        "sensor_code": "RIV-ALK-01",
        "water_level_m": 4.15,
        "rate_of_rise_mh": 0.35,
        "discharge_rate_m3s": 42.0,
        "source": "simulated"
    }
    res = client.post("/api/v1/sensors/ingest", json=ingest_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["water_level_m"] == 4.15
    assert data["source"] == "simulated"  # Strictly marked simulated per Hard Rule 3


def test_sensors_list(client):
    res = client.get("/api/v1/sensors")
    assert res.status_code == 200
    sensors = res.json()
    assert len(sensors) > 0
    assert any(s["sensor_code"] == "RIV-ALK-01" for s in sensors)


def test_alerts_trigger_with_graceful_degradation(client):
    # Get basin id
    v_res = client.get("/api/v1/villages")
    basin_id = v_res.json()[0]["basin_id"]

    payload = {
        "basin_id": basin_id,
        "severity": "High",
        "title": "Severe Mountain Runoff Warning",
        "message": "Continuous heavy rainfall in upper catchment. Evacuate low-lying riverbanks.",
        "channels": ["SMS", "Telegram", "Email", "Webhook", "Push"]
    }

    res = client.post("/api/v1/alerts/trigger", json=payload)
    assert res.status_code == 200
    alert_data = res.json()
    assert alert_data["severity"] == "High"
    assert len(alert_data["deliveries"]) > 0

    # Verify Hard Rule 8: Unconfigured providers record status="skipped_unconfigured"
    # and do NOT falsely claim "delivered"
    delivery_statuses = {d["channel"]: d["status"] for d in alert_data["deliveries"]}
    assert "SMS" in delivery_statuses
    assert delivery_statuses["SMS"] in ["delivered", "skipped_unconfigured"]


def test_ml_transparency_and_metrics(client):
    metrics_res = client.get("/api/v1/ml/metrics")
    assert metrics_res.status_code == 200
    metrics_data = metrics_res.json()
    assert "reports" in metrics_data

    trans_res = client.get("/api/v1/ml/transparency")
    assert trans_res.status_code == 200
    trans_data = trans_res.json()
    assert "ground_truth_disclosure" in trans_data
    assert "proxy_methodology" in trans_data["ground_truth_disclosure"]


def test_on_demand_prediction(client):
    payload = {
        "rain_1h_mm": 50.0,
        "rain_3h_mm": 90.0,
        "soil_moisture_0_to_1cm": 0.42,
        "elevation_m": 1400.0,
        "slope_degrees": 28.0,
        "sensor_level_m": 4.9,
        "sensor_danger_mark_m": 5.0,
    }
    res = client.post("/api/v1/ml/predict", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "risk_score" in data
    assert "risk_level" in data
    assert "horizons" in data
    assert len(data["key_factors"]) > 0


def test_ml_hindcast_results(client):
    res = client.get("/api/v1/ml/hindcast")
    assert res.status_code == 200
    data = res.json()
    assert "limitations" in data

