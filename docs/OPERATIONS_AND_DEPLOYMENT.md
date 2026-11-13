# PENELOPE Operations & Deployment Guide

## Quickstart (Local Development)

### 1. Booting with Docker Compose (Single Command)
```bash
make dev
```
This builds and starts:
- PostgreSQL 16 + PostGIS on `localhost:5432`
- Redis 7 on `localhost:6379`
- FastAPI backend on `http://localhost:8000`
- Next.js 14 frontend on `http://localhost:3000`
- Nginx reverse proxy on `http://localhost:80`

### 2. Running Locally (Without Docker)

#### Backend:
```bash
# Seed initial real OSM basins, villages, shelters, and sensors:
python -m apps.api.seed

# Start FastAPI server with live reload:
python -m uvicorn apps.api.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Frontend:
```bash
cd apps/web
pnpm dev
```
Open `http://localhost:3000` in your browser.

---

## 3. Running Verification Tests

```bash
# Backend and ML test suite (15 tests covering ingestion, ML, alerts, sensors, healthz):
pytest apps/api/tests ml/tests -v

# Frontend build verification:
cd apps/web && pnpm build
```

---

## 4. Retraining ML Models & Updating Metrics

```bash
# Runs full data synthesis, training, MLflow-lite JSON metrics export:
python -m ml.train
# or
make train
```

---

## 5. Alert Provider Configuration & Graceful Degradation (Hard Rule 8)

Configured via `.env`:

```ini
# Twilio SMS (Optional)
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_FROM_NUMBER=+1234567890

# Telegram Bot (Optional)
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrSTUvwxYZ
TELEGRAM_DEFAULT_CHAT_ID=-1001234567890

# SMTP Email (Optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=alerts@penelope-flood.org
SMTP_PASSWORD=app_password

# External Emergency Webhook (Optional)
WEBHOOK_ALERT_URL=https://emergency-services.state.gov.in/api/v1/webhook
```

**Graceful Degradation Guarantee:**
If any or all of the above credentials are omitted, the platform starts with 0 errors. Alert dispatch calls for unconfigured channels record the delivery status as `skipped_unconfigured` and log the reason in the database and audit trail. The UI shows the provider as disabled and never reports unverified deliveries.
