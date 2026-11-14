"""
PENELOPE Backend - Part 2 Automated Tests
Tests terrain pipeline, weather clustering, GloFAS river ingestion, circuit breaker resilience,
sensor HMAC authentication, and /v1/health/data endpoint.
"""

import os
import math
import hmac
import hashlib
import json
import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy import select, func

from apps.api.main import app
from apps.api.database import SessionLocal, init_db
from apps.api.models import Region, GridCell, WeatherObs, RiverObs, SensorDevice
from apps.api.ingestion.terrain import terrain_pipeline
from apps.api.ingestion.weather import weather_service
from apps.api.ingestion.river import river_service
from apps.api.ingestion.resilience import (
    CircuitBreaker, CircuitBreakerOpenException, cache, ingest_health, retry_with_backoff
)
from app.sim.sensors import run_sensor_simulation

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    init_db()
    with SessionLocal() as db:
        # Verify demo region exists
        reg = db.execute(select(Region)).scalars().first()
        if not reg:
            reg = Region(
                name="Test-Region",
                state="Uttarakhand",
                geom={"type": "Polygon", "coordinates": [[[79.5, 30.5], [79.6, 30.5], [79.6, 30.6], [79.5, 30.6], [79.5, 30.5]]]},
                centroid={"type": "Point", "coordinates": [79.55, 30.55]}
            )
            db.add(reg)
            db.commit()
    yield


# ============================================================================
# 1. CIRCUIT BREAKER & RESILIENCE TESTS
# ============================================================================
def test_circuit_breaker_transitions():
    cb = CircuitBreaker("test_provider", failure_threshold=2, recovery_time_sec=0.2)
    assert cb.state == "CLOSED"
    assert cb.can_execute() is True

    # Record 1 failure
    cb.record_failure(ValueError("err 1"))
    assert cb.state == "CLOSED"
    assert cb.can_execute() is True

    # Record 2nd failure -> Trips to OPEN
    cb.record_failure(ValueError("err 2"))
    assert cb.state == "OPEN"
    assert cb.can_execute() is False

    # Wait for recovery timeout
    import time
    time.sleep(0.25)
    assert cb.can_execute() is True
    assert cb.state == "HALF_OPEN"

    # Success in HALF_OPEN resets to CLOSED
    cb.record_success()
    assert cb.state == "CLOSED"
    assert cb.consecutive_failures == 0


def test_hybrid_cache():
    cache.set("test_key_123", {"value": 42}, ttl_sec=2)
    val = cache.get("test_key_123")
    assert val == {"value": 42}

    assert cache.get("non_existent_key") is None


# ============================================================================
# 2. TERRAIN PIPELINE TESTS
# ============================================================================
def test_terrain_grid_generation_and_topography():
    with SessionLocal() as db:
        region = db.execute(select(Region)).scalars().first()
        assert region is not None

        # Generate small 3x3 test grid (res=500m)
        cells = terrain_pipeline.generate_grid_for_region(region, res_m=500.0, max_cells=9)
        assert len(cells) > 0
        for c in cells:
            assert "lat" in c
            assert "lon" in c
            assert "polygon_coords" in c
            assert len(c["polygon_coords"]) == 5

        # Assign synthetic elevations
        for c in cells:
            c["elevation_m"] = 1500.0 + c["grid_i"] * 80.0 + c["grid_j"] * 40.0

        # Compute topographic features
        river_coords = [(region.center_lat, region.center_lon)]
        analyzed = terrain_pipeline.compute_topography(cells, river_coords)

        for c in analyzed:
            assert 0.0 <= c["slope_deg"] <= 90.0
            assert 0.0 <= c["aspect"] <= 360.0
            assert c["flow_accum"] >= 500.0
            assert not math.isnan(c["twi"])
            assert c["dist_to_river_m"] >= 0.0
            assert c["landcover"] in ("riverbed", "dense_forest", "alpine_meadow", "rocky_alpine", "steep_scarp", "terrace_agriculture")


@pytest.mark.asyncio
async def test_terrain_pipeline_idempotence():
    with SessionLocal() as db:
        region = db.execute(select(Region)).scalars().first()
        count1 = await terrain_pipeline.process_region(region, db, res_m=500.0)
        assert count1 > 0

        # Running again must be idempotent
        count2 = await terrain_pipeline.process_region(region, db, res_m=500.0)
        assert count2 == count1


# ============================================================================
# 3. WEATHER INGESTION TESTS
# ============================================================================
@pytest.mark.asyncio
async def test_weather_ingestion_clustering_and_lapse_rate():
    with SessionLocal() as db:
        region = db.execute(select(Region)).scalars().first()
        total_obs = await weather_service.ingest_weather_for_region(region, db)
        assert total_obs > 0

        # Verify records exist in database
        sample = db.execute(
            select(WeatherObs).where(WeatherObs.basin_id == region.id)
        ).scalars().first()
        assert sample is not None
        assert sample.precip_mm >= 0.0
        assert sample.humidity > 0.0
        assert sample.source == "open_meteo"


@pytest.mark.asyncio
async def test_historical_weather_backfill():
    # Test 5-day historical backfill
    records = await weather_service.backfill_historical(30.5, 79.5, start_date="2023-08-01", end_date="2023-08-06")
    assert len(records) >= 5
    for r in records:
        assert "date" in r
        assert "precip_mm" in r
        assert r["precip_mm"] >= 0.0


# ============================================================================
# 4. GLOFAS RIVER INGESTION TESTS
# ============================================================================
@pytest.mark.asyncio
async def test_glofas_river_ingestion():
    with SessionLocal() as db:
        region = db.execute(select(Region)).scalars().first()
        q_count = await river_service.ingest_river_for_region(region, db)
        assert q_count > 0

        latest = db.execute(
            select(RiverObs).where(RiverObs.source == "glofas").order_by(RiverObs.ts.desc())
        ).scalars().first()
        assert latest is not None
        assert latest.discharge_m3s >= 0.0
        assert latest.level_m > 0.0


# ============================================================================
# 5. SENSOR INGESTION & HMAC TESTS (POST /v1/sensors/readings)
# ============================================================================
def test_sensor_ingest_without_hmac():
    payload = {
        "sensor_code": "GAUGE-TEST-001",
        "water_level_m": 3.15,
        "discharge_m3s": 38.5,
        "rate_of_rise_mh": 0.08,
        "source": "sensor"
    }
    resp = client.post("/api/v1/sensors/readings", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["station_or_cell_id"] == "GAUGE-TEST-001"
    assert data["water_level_m"] == 3.15
    assert data["source"] == "sensor"


def test_sensor_ingest_with_valid_hmac():
    api_key = "device-secret-key-xyz"
    payload = {
        "sensor_code": "GAUGE-TEST-002",
        "water_level_m": 4.10,
        "discharge_m3s": 52.0,
        "rate_of_rise_mh": 0.18,
        "source": "sensor"
    }
    raw_body = json.dumps(payload, separators=(',', ':')).encode("utf-8")
    sig = hmac.new(api_key.encode(), raw_body, hashlib.sha256).hexdigest()

    resp = client.post(
        "/api/v1/sensors/readings",
        content=raw_body,
        headers={
            "Content-Type": "application/json",
            "X-API-Key": api_key,
            "X-Signature": sig
        }
    )
    assert resp.status_code == 201
    assert resp.json()["water_level_m"] == 4.10


def test_sensor_ingest_with_invalid_hmac_rejected():
    api_key = "device-secret-key-xyz"
    payload = {
        "sensor_code": "GAUGE-TEST-003",
        "water_level_m": 2.50,
        "source": "sensor"
    }
    raw_body = json.dumps(payload, separators=(',', ':')).encode("utf-8")

    resp = client.post(
        "/api/v1/sensors/readings",
        content=raw_body,
        headers={
            "Content-Type": "application/json",
            "X-API-Key": api_key,
            "X-Signature": "tampered_fake_signature"
        }
    )
    assert resp.status_code == 401
    assert "X-Signature mismatch" in resp.json()["detail"]


def test_simulated_sensors_runner():
    count = run_sensor_simulation(num_steps=2)
    assert count > 0

    with SessionLocal() as db:
        latest_sim = db.execute(
            select(RiverObs).where(RiverObs.source == "simulated").order_by(RiverObs.ts.desc())
        ).scalars().first()
        assert latest_sim is not None
        assert latest_sim.source == "simulated"


# ============================================================================
# 6. HEALTH DATA & STALENESS ENDPOINT TESTS
# ============================================================================
def test_health_data_endpoint():
    resp = client.get("/api/v1/health/data")
    assert resp.status_code == 200
    data = resp.json()
    assert "sources" in data
    assert "weather" in data["sources"]
    assert "glofas" in data["sources"]
    assert "sensor" in data["sources"]
    assert "terrain" in data["sources"]
    assert "database_totals" in data
    assert data["database_totals"]["grid_cells"] > 0
    assert data["database_totals"]["weather_observations"] > 0
    assert data["database_totals"]["river_observations"] > 0


# ============================================================================
# 7. LIVE SMOKE TEST (OPEN-METEO)
# ============================================================================
@pytest.mark.live
@pytest.mark.asyncio
async def test_live_open_meteo_smoke():
    if os.getenv("CI") == "true" or os.getenv("SKIP_LIVE_TESTS") == "true":
        pytest.skip("Skipping live smoke test in CI or offline environment")

    elevations = await terrain_pipeline.fetch_elevations_batch([(30.55, 79.55)])
    assert len(elevations) == 1
    assert elevations[0] > 500.0  # Himalayan elevation

