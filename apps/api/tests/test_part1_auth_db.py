"""
PENELOPE Backend - Part 1 Test Suite: DB Schema, PostGIS Geometries, Auth & RBAC
Tests:
1. User registration, login, JWT token lifecycle (access 15m, refresh 7d cookie).
2. RBAC role enforcement across all roles (citizen, tourist, authority, responder, ngo, admin).
3. PostGIS Geometry round-trips (Point, Polygon, MultiPolygon).
4. Seeding validation (>= 200 locations per region across Chamoli, Kullu, Wayanad).
5. Observability: X-Request-ID header verification.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select, func

from apps.api.main import app
from apps.api.database import SessionLocal, init_db
from apps.api.seed import seed_database
from apps.api.models import (
    User,
    Region,
    Location,
    GridCell,
    SensorDevice,
    WeatherObs,
    RiverObs,
    Alert
)
from apps.api.geo_types import (
    make_point_geojson,
    make_polygon_geojson,
    make_multipolygon_geojson,
    extract_lon_lat
)

client = TestClient(app)


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Ensure database schema is initialized and seeded before running tests."""
    init_db()
    seed_database()


# ============================================================================
# 1. AUTHENTICATION & TOKEN LIFECYCLE TESTS
# ============================================================================
def test_user_registration_and_duplicate_check():
    """Test user registration and 409 conflict on duplicate email."""
    test_email = "new_responder@penelope.org"
    # Ensure fresh state
    with SessionLocal() as db:
        existing = db.execute(select(User).where(User.email == test_email)).scalar_one_or_none()
        if existing:
            db.delete(existing)
            db.commit()

    reg_payload = {
        "email": test_email,
        "password": "SecurePassword123!",
        "name": "Arjun Singh",
        "role": "responder",
        "org": "SDRF Chamoli Unit"
    }
    resp = client.post("/api/v1/auth/register", json=reg_payload)
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert "access_token" in data
    assert data["user"]["email"] == test_email
    assert data["user"]["role"] == "responder"
    assert "refresh_token" in resp.cookies

    # Duplicate check
    dup_resp = client.post("/api/v1/auth/register", json=reg_payload)
    assert dup_resp.status_code == 409


def test_login_success_and_failure():
    """Test login with correct credentials and rejection on wrong password."""
    # Correct login
    login_payload = {
        "email": "authority@penelope.org",
        "password": "Penelope@2026!"
    }
    resp = client.post("/api/v1/auth/login", json=login_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["user"]["role"] == "authority"
    assert "refresh_token" in resp.cookies

    # Invalid password
    bad_login = {
        "email": "authority@penelope.org",
        "password": "WrongPassword!"
    }
    bad_resp = client.post("/api/v1/auth/login", json=bad_login)
    assert bad_resp.status_code == 401


def test_token_refresh_and_logout():
    """Test token refresh via httpOnly cookie and logout."""
    login_resp = client.post("/api/v1/auth/login", json={
        "email": "admin@penelope.org",
        "password": "Penelope@2026!"
    })
    assert login_resp.status_code == 200
    refresh_token = login_resp.cookies.get("refresh_token")
    assert refresh_token is not None

    # Refresh
    client.cookies.set("refresh_token", refresh_token)
    ref_resp = client.post("/api/v1/auth/refresh")
    assert ref_resp.status_code == 200
    assert "access_token" in ref_resp.json()

    # Logout
    logout_resp = client.post("/api/v1/auth/logout")
    assert logout_resp.status_code == 200


def test_get_current_user_profile():
    """Test /api/v1/auth/me with valid and invalid Bearer token."""
    login_resp = client.post("/api/v1/auth/login", json={
        "email": "ngo@penelope.org",
        "password": "Penelope@2026!"
    })
    token = login_resp.json()["access_token"]

    # Valid token
    me_resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == "ngo@penelope.org"
    assert me_resp.json()["role"] == "ngo"

    # Invalid token
    bad_resp = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer invalid.fake.token"})
    assert bad_resp.status_code == 401


# ============================================================================
# 2. RBAC ROLE ENFORCEMENT FOR ALL 6 ROLES
# ============================================================================
@pytest.mark.parametrize("role_email,expected_role", [
    ("citizen@penelope.org", "citizen"),
    ("tourist@penelope.org", "tourist"),
    ("authority@penelope.org", "authority"),
    ("responder@penelope.org", "responder"),
    ("ngo@penelope.org", "ngo"),
    ("admin@penelope.org", "admin"),
])
def test_all_six_roles_login_successfully(role_email, expected_role):
    """Verify that all 6 predefined roles authenticate properly."""
    resp = client.post("/api/v1/auth/login", json={
        "email": role_email,
        "password": "Penelope@2026!"
    })
    assert resp.status_code == 200
    assert resp.json()["user"]["role"] == expected_role


def test_rbac_authorization_barrier():
    """Verify that citizen cannot access authority endpoints, but authority can."""
    # 1. Citizen login
    cit_resp = client.post("/api/v1/auth/login", json={
        "email": "citizen@penelope.org",
        "password": "Penelope@2026!"
    })
    cit_token = cit_resp.json()["access_token"]

    # 2. Authority login
    auth_resp = client.post("/api/v1/auth/login", json={
        "email": "authority@penelope.org",
        "password": "Penelope@2026!"
    })
    auth_token = auth_resp.json()["access_token"]

    # Authority dispatches alert
    alert_payload = {
        "severity": "High",
        "title": "Evacuation Warning",
        "message": "Water levels rising at Vishnuprayag gauge",
        "channels": ["SMS", "Push"]
    }
    # When citizen attempts to dispatch alert -> 403 Forbidden
    blocked_resp = client.post(
        "/api/v1/alerts/dispatch",
        json=alert_payload,
        headers={"Authorization": f"Bearer {cit_token}"}
    )
    assert blocked_resp.status_code == 403

    # When authority dispatches alert -> 200 OK
    allowed_resp = client.post(
        "/api/v1/alerts/dispatch",
        json=alert_payload,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert allowed_resp.status_code == 200


# ============================================================================
# 3. POSTGIS / GEOMETRY ROUND-TRIP TESTS
# ============================================================================
def test_geometry_creation_and_coordinate_extraction():
    """Test Point, Polygon, and MultiPolygon geometry round-trips."""
    # Point
    pt = make_point_geojson(79.5442, 30.5543)
    assert pt["type"] == "Point"
    lon, lat = extract_lon_lat(pt)
    assert abs(lon - 79.5442) < 1e-4
    assert abs(lat - 30.5543) < 1e-4

    # WKT Point string extraction
    lon_wkt, lat_wkt = extract_lon_lat("POINT(77.1095 31.9579)")
    assert abs(lon_wkt - 77.1095) < 1e-4
    assert abs(lat_wkt - 31.9579) < 1e-4

    # Polygon & MultiPolygon
    poly_coords = [[[79.1, 30.1], [79.9, 30.1], [79.9, 30.9], [79.1, 30.9], [79.1, 30.1]]]
    poly = make_polygon_geojson(poly_coords)
    assert poly["type"] == "Polygon"

    multipoly = make_multipolygon_geojson([poly_coords])
    assert multipoly["type"] == "MultiPolygon"


# ============================================================================
# 4. SEED DATA VALIDATION: >= 200 LOCATIONS PER REGION
# ============================================================================
def test_seed_populated_three_regions_with_at_least_200_locations_each():
    """Verify that all 3 demo regions have >= 200 real locations populated."""
    with SessionLocal() as db:
        regions = db.execute(select(Region)).scalars().all()
        assert len(regions) == 3, f"Expected 3 regions, found {len(regions)}"

        region_names = {r.name for r in regions}
        assert "Uttarakhand-Chamoli" in region_names
        assert "Himachal-Kullu" in region_names
        assert "Kerala-Wayanad" in region_names

        for r in regions:
            count = db.execute(select(func.count(Location.id)).where(Location.region_id == r.id)).scalar()
            assert count >= 200, f"Region {r.name} has only {count} locations; expected >= 200"


# ============================================================================
# 5. OBSERVABILITY: X-REQUEST-ID HEADER
# ============================================================================
def test_request_id_middleware_assigns_header():
    """Verify that X-Request-ID is attached to every HTTP response."""
    resp = client.get("/api/v1/healthz")
    assert resp.status_code == 200
    assert "X-Request-ID" in resp.headers
    assert len(resp.headers["X-Request-ID"]) > 10

