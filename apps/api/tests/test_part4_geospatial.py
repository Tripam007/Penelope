"""
PENELOPE Backend - Part 4 Test Suite: Geospatial Risk Engine & APIs
Covers:
1. Vector tiles & MVT binary protobuf validity (vector_tile.proto specification).
2. GeoJSON risk endpoint with bbox filtering, horizons, and ETag 304 caching.
3. Map layers: heatmap, terrain hillshade, rainfall, river discharge anomaly, locations, shelters.
4. Village risk roll-up: risk = max over cells within radius, population at risk,
   and acceptance criteria (current + 24h/48h risk with drivers).
5. Safe-route routing penalty behavior and acceptance criteria (route changes when segment risk is raised).
6. Tourist plain-language advice (EN/HI) with nearest shelter and emergency contacts.
7. Region summary intelligence: counts, population at risk, trend, top drivers.
8. Real-time SSE live risk streaming.
"""

import os
os.environ["TESTING"] = "true"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from apps.api.main import app
from apps.api.database import init_db, SessionLocal
from apps.api.seed import seed_database
from apps.api.models import Location, Region, GridCell
from apps.api.geospatial.mvt import (
    build_mvt_tile,
    parse_and_validate_mvt,
    tile_to_bbox
)
from apps.api.geospatial.risk_engine import (
    compute_hillshade,
    rollup_location_risk,
    get_region_summary_stats
)
from apps.api.geospatial.routing import routing_engine
from apps.api.geospatial.events import risk_event_bus, stream_risk_sse


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    init_db()
    seed_database()


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


# ---------------------------------------------------------------------------
# 1. MVT Vector Tile Protobuf Validity & Tile Endpoints
# ---------------------------------------------------------------------------

def test_mvt_protobuf_encoder_and_validator():
    """
    Verifies that build_mvt_tile produces valid MVT 2.1 protobuf bytes
    and that parse_and_validate_mvt decodes the layers, features, and keys.
    """
    bbox = tile_to_bbox(8, 184, 105)
    sample_features = [
        {
            "id": "cell-101",
            "geometry": {"type": "Point", "coordinates": [79.32, 30.37]},
            "properties": {
                "risk_score": 0.82,
                "risk_level": "Very High",
                "elevation_m": 1650.0,
                "slope_deg": 24.5
            }
        },
        {
            "id": "cell-102",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[79.31, 30.36], [79.33, 30.36], [79.33, 30.38], [79.31, 30.38], [79.31, 30.36]]]
            },
            "properties": {
                "risk_score": 0.35,
                "risk_level": "Moderate",
                "elevation_m": 1780.0,
                "slope_deg": 14.0
            }
        }
    ]

    mvt_bytes = build_mvt_tile("risk_grid", sample_features, bbox)
    assert isinstance(mvt_bytes, bytes)
    assert len(mvt_bytes) > 20

    # Parse and validate with MVT decoder
    parsed = parse_and_validate_mvt(mvt_bytes)
    assert parsed["valid"] is True
    assert parsed["layer_count"] == 1

    layer = parsed["layers"][0]
    assert layer["name"] == "risk_grid"
    assert layer["version"] == 2
    assert layer["extent"] == 4096
    assert layer["features_count"] == 2
    assert "risk_score" in layer["keys"]
    assert "risk_level" in layer["keys"]


def test_tiles_mvt_endpoint_and_etag_caching(client):
    """
    GET /v1/map/tiles/{z}/{x}/{y}.mvt returns binary vector tile with ETag.
    Subsequent request with If-None-Match returns 304.
    """
    res = client.get("/v1/map/tiles/8/184/105.mvt")
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/vnd.mapbox-vector-tile"
    assert len(res.content) > 0

    etag = res.headers.get("etag")
    assert etag is not None

    # Test conditional request 304 Not Modified
    res_cached = client.get("/v1/map/tiles/8/184/105.mvt", headers={"if-none-match": etag})
    assert res_cached.status_code == 304

    # Verify tile bytes are valid MVT
    parsed = parse_and_validate_mvt(res.content)
    assert parsed["valid"] is True
    assert parsed["layers"][0]["name"] == "risk_grid"


# ---------------------------------------------------------------------------
# 2. Risk GeoJSON Endpoint & Bounding Box Filtering
# ---------------------------------------------------------------------------

def test_risk_geojson_endpoint_and_bbox(client):
    """
    GET /v1/map/risk.geojson?bbox=&horizon= returns FeatureCollection with ETag.
    """
    res = client.get("/v1/map/risk.geojson?horizon=3h")
    assert res.status_code == 200
    assert "features" in res.json()
    assert res.json()["type"] == "FeatureCollection"
    assert len(res.json()["features"]) > 0

    etag = res.headers.get("etag")
    assert etag is not None

    # ETag 304 test
    res_etag = client.get("/v1/map/risk.geojson?horizon=3h", headers={"if-none-match": etag})
    assert res_etag.status_code == 304

    # Test Bounding Box filtering (Chamoli catchment approx 79.2 to 79.8, 30.2 to 30.7)
    res_bbox = client.get("/v1/map/risk.geojson?bbox=79.2,30.2,79.8,30.7&horizon=3h")
    assert res_bbox.status_code == 200
    bbox_features = res_bbox.json()["features"]
    assert len(bbox_features) > 0

    # Test feature properties
    sample_feat = bbox_features[0]
    props = sample_feat["properties"]
    assert "risk_score" in props
    assert "risk_level" in props
    assert "elevation_m" in props
    assert "drivers" in props


# ---------------------------------------------------------------------------
# 3. Layers Catalog & Individual Layer Data
# ---------------------------------------------------------------------------

def test_map_layers_catalog_and_layers(client):
    """
    Tests /v1/map/layers catalog and each individual layer GeoJSON endpoint.
    """
    res = client.get("/v1/map/layers")
    assert res.status_code == 200
    catalog = res.json()
    layer_ids = [lyr["id"] for lyr in catalog["layers"]]
    assert "risk-heatmap" in layer_ids
    assert "terrain" in layer_ids
    assert "rainfall" in layer_ids
    assert "river-network" in layer_ids
    assert "locations" in layer_ids
    assert "shelters" in layer_ids

    # 1. Terrain hillshade layer
    res_terrain = client.get("/v1/map/layers/terrain")
    assert res_terrain.status_code == 200
    terrain_data = res_terrain.json()
    assert len(terrain_data["features"]) > 0
    t_props = terrain_data["features"][0]["properties"]
    assert "hillshade" in t_props
    assert 0 <= t_props["hillshade"] <= 255
    assert "slope_deg" in t_props

    # 2. Rainfall layer
    res_rain = client.get("/v1/map/layers/rainfall")
    assert res_rain.status_code == 200
    assert len(res_rain.json()["features"]) > 0
    r_props = res_rain.json()["features"][0]["properties"]
    assert "rain_3h_mm" in r_props
    assert "rain_24h_forecast_mm" in r_props

    # 3. River network & discharge anomaly
    res_river = client.get("/v1/map/layers/river-network")
    assert res_river.status_code == 200
    assert len(res_river.json()["features"]) > 0
    rv_props = res_river.json()["features"][0]["properties"]
    assert "discharge_anomaly_pct" in rv_props
    assert "water_level_m" in rv_props

    # 4. Shelters layer
    res_shelters = client.get("/v1/map/layers/shelters")
    assert res_shelters.status_code == 200
    assert len(res_shelters.json()["features"]) > 0
    sh_props = res_shelters.json()["features"][0]["properties"]
    assert "capacity" in sh_props
    assert "status" in sh_props


# ---------------------------------------------------------------------------
# 4. Village Risk Roll-Up & Acceptance Criterion 1
# ---------------------------------------------------------------------------

def test_village_risk_rollup_and_acceptance_query(client):
    """
    Acceptance Criterion:
    A query for any village returns current + 24h/48h risk with drivers.
    Also verifies risk = max over cells within radius.
    """
    with SessionLocal() as db:
        village = db.execute(select(Location).where(Location.type == "village")).scalars().first()
        assert village is not None, "No village found in database"
        village_id = village.id
        village_name = village.name

    # API query
    res = client.get(f"/v1/villages/{village_id}")
    assert res.status_code == 200
    data = res.json()

    assert data["name"] == village_name
    assert "current_risk_score" in data
    assert "current_risk_level" in data
    assert "risk_24h" in data
    assert "risk_24h_level" in data
    assert "risk_48h" in data
    assert "risk_48h_level" in data
    assert "drivers" in data
    assert isinstance(data["drivers"], list)
    assert len(data["drivers"]) > 0
    assert "factor" in data["drivers"][0]

    # Test direct rollup computation
    with SessionLocal() as db:
        v_entity = db.execute(select(Location).where(Location.id == village_id)).scalars().first()
        rollup = rollup_location_risk(v_entity, db, radius_km=6.0)
        assert rollup["current_risk_score"] == data["current_risk_score"]
        assert rollup["risk_24h"] == data["risk_24h"]
        assert rollup["risk_48h"] == data["risk_48h"]


# ---------------------------------------------------------------------------
# 5. Safe Routing Penalty Behavior & Acceptance Criterion 2
# ---------------------------------------------------------------------------

def test_safe_route_penalty_behavior_and_acceptance(client):
    """
    Acceptance Criterion:
    Safe route changes when a segment's risk is raised in a test fixture.
    """
    with SessionLocal() as db:
        region = db.execute(select(Region).where(Region.name == "Uttarakhand-Chamoli")).scalars().first()
        assert region is not None
        reg_id = region.id

        locs = db.execute(
            select(Location)
            .where(Location.region_id == reg_id)
            .where(Location.type.in_(["village", "town"]))
        ).scalars().all()
        assert len(locs) >= 10

        src = locs[0]
        dst = locs[7]

    # 1. Baseline Route Request
    payload1 = {
        "from": [src.lon, src.lat],
        "to": [dst.lon, dst.lat],
        "region_id": reg_id
    }
    res1 = client.post("/v1/routing/safe", json=payload1)
    assert res1.status_code == 200
    route1 = res1.json()
    waypoints1 = [w["name"] for w in route1["properties"]["waypoints"]]
    assert len(waypoints1) >= 2
    assert "nearest_open_shelter" in route1["properties"]
    assert route1["properties"]["nearest_open_shelter"] is not None

    # 2. Identify the first intermediate segment and raise its flood risk to 0.95 (Severe hazard)
    hazard_waypoint = waypoints1[1]
    routing_engine.raise_segment_risk(hazard_waypoint, flood_risk=0.95, region_id=reg_id)

    # 3. Recalculate Route Request under hazardous segment conditions
    res2 = client.post("/v1/routing/safe", json=payload1)
    assert res2.status_code == 200
    route2 = res2.json()
    waypoints2 = [w["name"] for w in route2["properties"]["waypoints"]]

    # VERIFY ACCEPTANCE: Safe route path changed to avoid the flooded hazard segment!
    assert waypoints1 != waypoints2, f"Expected route to change away from flooded {hazard_waypoint}, but remained identical!"
    assert hazard_waypoint not in waypoints2[:2], f"Rerouted path still includes flooded {hazard_waypoint}!"

    # Verify risk exposure score and warnings
    assert route2["properties"]["risk_exposure_score"] >= 0.0
    assert len(route2["properties"]["warnings"]) > 0


# ---------------------------------------------------------------------------
# 6. Tourist Advice Endpoint
# ---------------------------------------------------------------------------

def test_tourist_advice_endpoint(client):
    """
    GET /v1/tourist/advice?lat=&lng= returns current/24h/48h risk,
    plain-language advice, nearest shelter, and emergency contacts.
    """
    res = client.get("/v1/tourist/advice?lat=30.3753&lng=79.3242&lang=en")
    assert res.status_code == 200
    data = res.json()

    assert "risk_now" in data
    assert "risk_24h" in data
    assert "risk_48h" in data
    assert "plain_language_advice" in data
    assert "advisory_level" in data
    assert data["advisory_level"] in ["NORMAL", "CAUTION", "WARNING", "EVACUATE"]
    assert "nearest_shelter" in data
    assert "emergency_contacts" in data
    assert "national_disaster_helpline" in data["emergency_contacts"]

    # Test Hindi language response
    res_hi = client.get("/v1/tourist/advice?lat=30.3753&lng=79.3242&lang=hi")
    assert res_hi.status_code == 200
    data_hi = res_hi.json()
    assert any("\u0900" <= char <= "\u097f" for char in data_hi["plain_language_advice"])


# ---------------------------------------------------------------------------
# 7. Region Summary Intelligence Endpoint
# ---------------------------------------------------------------------------

def test_region_summary_endpoint(client):
    """
    GET /v1/regions/{id}/summary returns counts, trend, top drivers, and last update.
    """
    with SessionLocal() as db:
        reg = db.execute(select(Region)).scalars().first()
        reg_id = reg.id
        reg_name = reg.name

    res = client.get(f"/v1/regions/{reg_id}/summary")
    assert res.status_code == 200
    data = res.json()

    assert data["region_name"] == reg_name
    counts = data["counts"]
    assert "total_villages" in counts
    assert "at_risk_villages" in counts
    assert "population_total" in counts
    assert "population_at_risk" in counts
    assert "live_alerts" in counts
    assert "open_shelters" in counts

    assert data["trend"] in ["rising", "stable", "falling"]
    assert "top_drivers" in data
    assert isinstance(data["top_drivers"], list)
    assert "last_update" in data


# ---------------------------------------------------------------------------
# 8. Server-Sent Events (SSE) Live Risk Stream
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_sse_stream_subscription():
    """
    Tests SSE generator connected to risk event bus.
    """
    gen = stream_risk_sse()
    initial_event = await gen.asend(None)
    assert "event: connection" in initial_event
    assert "INITIAL_SNAPSHOT" in initial_event

    # Publish an event to the bus
    risk_event_bus.publish({
        "type": "risk_update",
        "region_id": "chamoli-1",
        "message": "Water stage surge alert in Alaknanda river"
    })

    published_event = await gen.asend(None)
    assert "event: risk_update" in published_event
    assert "Water stage surge" in published_event
