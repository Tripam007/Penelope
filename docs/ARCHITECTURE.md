# PENELOPE Architecture & Engineering Specification

> **Tagline:** Data today. Safer tomorrows.  
> **Pillars:** Predict · Prepare · Protect

PENELOPE is an AI-powered flash-flood prediction and early-warning platform engineered specifically for mountainous and steep terrain catchments (such as the Himalayas and Western Ghats).

```
+-----------------------------------------------------------------------------------+
|                                 DATA SOURCES                                      |
|  Open-Meteo Weather (Hourly Precip, Rain, Showers, Multi-depth Soil Moisture)    |
|  Open-Meteo Flood (GloFAS Daily River Discharge, Mean, Max, Anomaly Percentile)    |
|  Open-Meteo Elevation / SRTM DEM (Elevation, Multi-direction Slope Gradient)      |
|  OpenStreetMap / Overpass (Villages, Topography, Safe Evacuation Shelters, Roads) |
|  River-Gauge IoT Telemetry (Live REST Ingest / Clearly Labeled SIM Generator)    |
+------------------------------------------+----------------------------------------+
                                           |
                                           v
+-----------------------------------------------------------------------------------+
|                        PROCESSING & INGESTION LAYER                               |
|  APScheduler Ingestion Daemon (Multi-basin Scheduled Cycles)                     |
|  Antecedent Precipitation Index (API 7-Day Exponential Decay Calculation)        |
|  Horn's Algorithm Digital Elevation Model Slope Gradient Processor              |
|  Simulated Sensor Generator (Enforces source="simulated" & UI [SIM] Badge)       |
+------------------------------------------+----------------------------------------+
                                           |
                                           v
+-----------------------------------------------------------------------------------+
|                          AI / ML PREDICTION ENGINE                                |
|  Tabular Multi-Horizon Model: LightGBM Gradient Boosted Decision Trees           |
|    - 1h, 3h, 6h, 24h Flash-Flood Hazard Probabilities                            |
|    - Calibrated against IMD Heavy Rain (>=64.5mm) & GloFAS (>92%) Proxy Labels   |
|  Baseline Tabular Model: Scikit-Learn Random Forest Classifier                   |
|  Temporal Sequence Model: 2-Layer Hydrology LSTM (24-Hour Stage Trajectory)      |
|  MLflow-Lite Metrics Registry: JSON Reports (ROC-AUC, PR-AUC, F1, Brier Score)   |
|  In-Flight Feature Contributions & Explainability Engine                        |
+------------------------------------------+----------------------------------------+
                                           |
                                           v
+-----------------------------------------------------------------------------------+
|                        RISK MAPPING & AUTHORITY ENGINE                            |
|  4-Tier Village Risk Categorization: Low (<25%), Moderate, High, Very High (>80%) |
|  Safe Evacuation Shelter Routing with Elevation Gain Optimization                |
|  Multi-Channel Alert Dispatcher (Twilio SMS, Telegram, SMTP Email, Webhook, Push) |
|  Strict Delivery Status Auditing (Delivered, Failed, Skipped Unconfigured)       |
+------------------------------------------+----------------------------------------+
                                           |
                      +--------------------+--------------------+
                      |                                         |
                      v                                         v
+-------------------------------------+   +-------------------------------------+
|        FASTAPI BACKEND API          |   |       NEXT.JS 14 WEB APP            |
|  REST Endpoints (/api/v1/...)       |   |  Interactive MapLibre GL JS Map     |
|  Live WebSocket Telemetry (/ws)     |   |  Bilingual UI (English & Hindi)     |
|  Server-Sent Events (/events/sse)   |   |  Authority Emergency Command Modal  |
|  OpenAPI Interactive Documentation  |   |  Offline-Ready PWA Manifest         |
+-------------------------------------+   +-------------------------------------+
```

## Repository Structure

```
/
├── apps/
│   ├── api/                 # FastAPI Python 3.11 Backend
│   │   ├── alerts/          # Alert Dispatcher with graceful degradation
│   │   ├── ingestion/       # Open-Meteo, OSM, Sensor Simulator, APScheduler
│   │   ├── routes/          # Health, Map, Villages, Sensors, Alerts, ML, WS
│   │   ├── database.py      # SQLAlchemy 2.0 engine & session
│   │   ├── models.py        # Declarative DB models (Basins, Villages, Shelters)
│   │   ├── schemas.py       # Pydantic v2 strict schemas
│   │   ├── seed.py          # Real OSM & terrain data seeder
│   │   └── main.py          # FastAPI application entrypoint
│   └── web/                 # Next.js 14 App Router Frontend
│       ├── public/          # PWA manifest, SVG icons
│       └── src/
│           ├── app/         # App router layout, page, styles, providers
│           ├── components/  # MapLibre map, Village drawer, Sensor monitor, Authority modal
│           ├── lib/         # Zustand store, TanStack Query API hooks, utils
│           └── messages/    # English & Hindi i18n translation bundles
├── ml/                      # Machine Learning Training & Inference
│   ├── models/              # Serialized binaries (.joblib, .npz) & MLflow-lite JSONs
│   ├── dataset.py           # Synthetic & semi-empirical hydrology generator
│   ├── features.py          # API index, Horn's slope, feature vector extraction
│   ├── proxy_labels.py      # IMD/CWC hydro-meteorological proxy labeling
│   ├── lstm_model.py        # Hydrology sequence LSTM architecture & inference
│   ├── train.py             # Unified model training & benchmark evaluator
│   └── predictor.py         # Multi-horizon risk scoring & explainability
├── infra/                   # Docker Compose & Nginx Reverse Proxy
│   ├── docker/              # Dockerfiles for API and Web
│   └── nginx/               # Nginx reverse proxy routing
├── docs/                    # Architectural, API & ML Documentation
├── Makefile                 # Unified make dev / test / train / seed workflow
└── docker-compose.yml       # Production container orchestration
```

