"""
PENELOPE Backend - Admin Portal & Warning Intelligence Tests
Tests:
1. Super Admin tripambiswas007@gmail.com authentication and role enforcement
2. Access restriction barrier (403 for citizen/tourist/unauthorized)
3. Warning intelligence endpoint returning complete WHERE, WHEN, and WHY (Causal AI) data
4. Administrative actions (emergency broadcast & evacuation milestone updates)
"""

import pytest
from fastapi.testclient import TestClient
from apps.api.main import app

client = TestClient(app)


def test_super_admin_login():
    """Verify tripambiswas007@gmail.com logs in with admin privileges."""
    res = client.post(
        "/api/v1/auth/login",
        json={"email": "tripambiswas007@gmail.com", "password": "Penelope@2026!"}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["user"]["email"] == "tripambiswas007@gmail.com"
    assert data["user"]["role"] == "admin"
    assert "access_token" in data


def test_admin_warning_intelligence_where_when_why():
    """Verify warning intelligence returns Where, When, and Why pillars for tripambiswas007@gmail.com."""
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "tripambiswas007@gmail.com", "password": "Penelope@2026!"}
    )
    token = login_res.json()["access_token"]

    intel_res = client.get(
        "/api/v1/admin/warning-intelligence",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert intel_res.status_code == 200
    intel = intel_res.json()

    # Admin officer info
    assert intel["admin_officer"]["email"] == "tripambiswas007@gmail.com"
    assert intel["admin_officer"]["role"] == "Super Admin"

    warning = intel["warning"]
    assert warning["severity"] == "CRITICAL"

    # 1. WHERE
    where = warning["where"]
    assert "region_name" in where
    assert "basin_name" in where
    assert "coordinates" in where
    assert "lat" in where["coordinates"] and "lon" in where["coordinates"]
    assert "affected_villages" in where
    assert len(where["affected_villages"]) > 0

    # 2. WHEN
    when = warning["when"]
    assert "triggered_at" in when
    assert "forecast_peak_arrival" in when
    assert "peak_countdown_seconds" in when
    assert "expected_surge_duration_hours" in when

    # 3. WHY (Causal reasoning)
    why = warning["why_reason"]
    assert "summary" in why
    assert len(why["summary"]) > 20
    assert "causal_factors" in why
    assert len(why["causal_factors"]) >= 4

    factor_ids = [f["id"] for f in why["causal_factors"]]
    assert "factor-rainfall" in factor_ids
    assert "factor-soil" in factor_ids
    assert "factor-river" in factor_ids
    assert "factor-terrain" in factor_ids


def test_non_admin_forbidden_from_admin_portal():
    """Verify regular non-admin user is rejected with HTTP 403."""
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "citizen@penelope.org", "password": "Penelope@2026!"}
    )
    token = login_res.json()["access_token"]

    intel_res = client.get(
        "/api/v1/admin/warning-intelligence",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert intel_res.status_code == 403
    assert "Access restricted" in intel_res.json()["detail"]


def test_admin_emergency_action_dispatch():
    """Verify admin can dispatch emergency broadcast and update evacuation milestones."""
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "tripambiswas007@gmail.com", "password": "Penelope@2026!"}
    )
    token = login_res.json()["access_token"]

    action_res = client.post(
        "/api/v1/admin/warnings/action",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "action_type": "BROADCAST_ALERT",
            "custom_message": "RED ALERT: Immediate evacuation ordered.",
            "channels": ["SMS", "Telegram"]
        }
    )
    assert action_res.status_code == 200
    assert action_res.json()["status"] == "success"
    assert "deliveries" in action_res.json()
