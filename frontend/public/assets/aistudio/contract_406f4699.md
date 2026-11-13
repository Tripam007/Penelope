# API Contract: Flash Flood Prediction System (Team Penelope)

**Owner:** Member 4 (Integration Lead). Nobody changes this file without telling the whole team.

**Base URL (local):** `http://localhost:8000`
**Format:** JSON only. All times in ISO 8601 UTC. CORS enabled on the backend so the frontend can call it.

---

## Shared Rules

- `risk` is always exactly one of: `"Low"`, `"Moderate"`, `"High"`, `"Very High"`
- `score` is a float from `0.0` to `1.0`
- Risk mapping: `0-0.25` Low, `0.25-0.5` Moderate, `0.5-0.75` High, `0.75-1.0` Very High
- Colors (frontend): Low = green, Moderate = yellow, High = orange, Very High = red
- Alerts fire when risk is `High` or `Very High`
- Errors always return: `{"error": "message"}` with a proper HTTP status

---

## Data Model: Village

```json
{
  "id": 1,
  "name": "Kedarpur",
  "lat": 30.3,
  "lon": 78.0,
  "population": 1200,
  "risk": "High",
  "score": 0.82,
  "rainfall_mm_24h": 96,
  "updated": "2026-11-13T10:00:00Z"
}
```

---

## Endpoints

### 1. GET `/villages`
Returns all hardcoded villages (8-10) with current risk. Used by the map.

**Response 200:**
```json
[ { "...Village object..." }, { "...Village object..." } ]
```

### 2. GET `/risk?lat=30.3&lon=78.0`
Returns risk for one location.

**Response 200:**
```json
{
  "lat": 30.3,
  "lon": 78.0,
  "risk": "High",
  "score": 0.82,
  "rainfall_mm_24h": 96,
  "updated": "2026-11-13T10:00:00Z"
}
```

**Response 400:** `{"error": "lat and lon are required"}`

### 3. GET `/alerts`
Returns active alerts, newest first.

**Response 200:**
```json
[
  {
    "id": 1,
    "village": "Kedarpur",
    "risk": "Very High",
    "message": "Evacuate low-lying areas immediately",
    "time": "2026-11-13T10:05:00Z"
  }
]
```

### 4. POST `/simulate`
Powers the "simulate heavy rain" button. Overrides rainfall for one village and returns the new risk. Also triggers an alert if risk is High or Very High.

**Request:**
```json
{ "village_id": 1, "rainfall_mm": 150 }
```

**Response 200:** same shape as a Village object (with updated `risk`, `score`, `rainfall_mm_24h`).

**Response 404:** `{"error": "village not found"}`

### 5. POST `/reset`
Clears simulations and alerts, back to live data.

**Response 200:** `{"status": "ok"}`

---

## ML Function (Member 1 -> Member 2)

File: `ml/predict.py`

```python
def predict(lat: float, lon: float, rainfall_mm: float) -> dict:
    """Returns {"risk": "High", "score": 0.82}"""
```

Member 1 delivers this function (plus the saved model file) early, even with a dummy rule-based version, so Member 2 is never blocked.

---

## Mock Data (Member 3 uses until backend is ready)

File: `frontend/mock.json`
Must match the `/villages` and `/alerts` shapes exactly. Member 4 creates it in the first 2 hours.

---

## Suggested Repo Structure

```
/ml          -> Member 1 (train.py, predict.py, model.pkl, data/)
/backend     -> Member 2 (main.py, alerts.py, villages.py, .env.example)
/frontend    -> Member 3 (React or Streamlit app, mock.json)
contract.md  -> this file
README.md    -> Member 4
```

## Git Rules

- `main` is always working. Work on your own branch (`ml`, `backend`, `frontend`).
- Commit after every working step. Merge to `main` only after testing.
- Never commit `.env` or API keys.

## Change Log

| Time | Change | Who |
|------|--------|-----|
| 0h | Initial contract | Member 4 |
