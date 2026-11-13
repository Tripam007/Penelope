# PENELOPE API Reference (v1)

Base URL: `http://localhost:8000/api/v1`  
Interactive OpenAPI Swagger Docs: `http://localhost:8000/docs`

---

### 1. Health & Readiness
- `GET /healthz`
  - Returns overall platform health, database connectivity type, APScheduler running status, loaded ML model status, and graceful degradation status of alert providers (Twilio, Telegram, SMTP, Webhooks).

### 2. Map & Geospatial
- `GET /api/v1/map/geojson`
  - Returns a GeoJSON `FeatureCollection` containing:
    - **Villages:** Point features with `risk_score` (0.0 - 1.0), `risk_level` (Low, Moderate, High, Very High), elevation, slope, and population.
    - **River Sensors:** Point features with current `water_level_m`, `danger_level_m`, `danger_ratio`, `is_simulated` boolean, and `source` (`"live"` or `"simulated"`).
    - **Shelters:** Safe elevation relief shelters with capacity and contact information.
    - **Evacuation Routes:** LineString features connecting high-risk villages to higher-elevation designated shelters.

### 3. Villages
- `GET /api/v1/villages`
  - Parameters: `basin_id` (optional), `risk_level` (optional), `search` (optional).
  - Returns list of villages ordered by current flood risk score descending.
- `GET /api/v1/villages/{village_id}`
  - Returns comprehensive diagnostic profile for a specific village, including terrain metrics, assigned safe shelter details, elevation gain, and recent alerts.

### 4. River Sensors (Hard Rule 3)
- `POST /api/v1/sensors/ingest`
  - Ingests real IoT gauge readings or simulated readings.
  - Request Body:
    ```json
    {
      "sensor_code": "RIV-ALK-01",
      "water_level_m": 4.15,
      "rate_of_rise_mh": 0.35,
      "discharge_rate_m3s": 42.0,
      "source": "live"
    }
    ```
- `GET /api/v1/sensors`
  - Lists all gauge stations with latest telemetry, saturation percentage, and simulation status.
- `GET /api/v1/sensors/{sensor_code}/readings`
  - Parameters: `limit` (default: 50).
  - Time-series readings for a sensor.
- `POST /api/v1/sensors/simulate-surge?sensor_code=...`
  - On-demand trigger to simulate an upstream cloudburst runoff surge on a simulated sensor. Returns `source="simulated"` and `sim_badge: true`.

### 5. Alerts & Disaster Authority Dispatch (Hard Rules 4 & 8)
- `GET /api/v1/alerts`
  - Lists past alerts and active warnings with full delivery audit trail.
- `GET /api/v1/alerts/active`
  - Lists currently active emergency advisories.
- `POST /api/v1/alerts/trigger`
  - Command endpoint for NDRF/SDRF/DDMA authorities.
  - Request Body:
    ```json
    {
      "basin_id": "...",
      "village_id": "...",
      "severity": "High",
      "title": "Flash-Flood Early Warning - Runoff Surge",
      "message": "Immediate evacuation advisory for low-lying riverbanks.",
      "channels": ["SMS", "Telegram", "Email", "Webhook", "Push"]
    }
    ```
  - Audit Trail: Returns per-channel delivery status (`delivered`, `failed`, `skipped_unconfigured`). Never reports `delivered` unless verified by provider API.
- `POST /api/v1/alerts/{alert_id}/resolve`
  - Marks an active alert as resolved.

### 6. AI / ML Insights & Transparency (Hard Rule 4)
- `GET /api/v1/ml/metrics`
  - Returns MLflow-lite JSON metrics reports for LightGBM, Random Forest baseline, and PyTorch LSTM.
- `POST /api/v1/ml/predict`
  - On-demand inference with feature contributions and 1h, 3h, 6h, 24h multi-horizon risk scoring.
- `GET /api/v1/ml/transparency`
  - Returns the official model honesty statement and IMD/CWC/NDMA advisory notices.

### 7. Real-Time Streaming
- `WebSocket /api/v1/ws`
  - Streams real-time `SENSOR_TELEMETRY` and `ALERT_TRIGGERED` events to connected browser and authority clients.
- `GET /api/v1/events/sse`
  - Server-Sent Events alternative for lightweight clients.
