"""
PENELOPE Backend - Configuration Management
Pydantic v2 Settings with strict typing and graceful degradation.
"""

from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # General
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "penelope-super-secret-key-change-in-production-2026"

    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000"
    ]

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://penelope:penelope_dev_secret@localhost:5432/penelope_db"
    DATABASE_SYNC_URL: str = "postgresql://penelope:penelope_dev_secret@localhost:5432/penelope_db"
    SQLITE_FALLBACK_URL: str = "sqlite+aiosqlite:///./penelope.db"
    USE_SQLITE_FALLBACK: bool = True

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Ingestion & External APIs
    OPEN_METEO_FORECAST_URL: str = "https://api.open-meteo.com/v1/forecast"
    OPEN_METEO_FLOOD_URL: str = "https://flood-api.open-meteo.com/v1/flood"
    OPEN_METEO_ELEVATION_URL: str = "https://api.open-meteo.com/v1/elevation"
    OVERPASS_API_URL: str = "https://overpass-api.de/api/interpreter"

    # Simulation Daemon
    SIMULATE_SENSORS: bool = True
    SIMULATION_INTERVAL_SECONDS: int = 15

    # ML
    MODEL_DIR: str = "ml/models"
    ACTIVE_TABULAR_MODEL: str = "lightgbm_flood_classifier.joblib"
    ACTIVE_LSTM_MODEL: str = "lstm_hydrology_model.npz"

    # Alert Providers (Optional - Graceful Degradation)
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_FROM_NUMBER: Optional[str] = None

    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_DEFAULT_CHAT_ID: Optional[str] = None

    SMTP_HOST: Optional[str] = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_EMAIL: str = "alerts@penelope-flood.org"

    WEBHOOK_ALERT_URL: Optional[str] = None

    # Helper properties for graceful degradation detection
    @property
    def is_twilio_configured(self) -> bool:
        return bool(self.TWILIO_ACCOUNT_SID and self.TWILIO_AUTH_TOKEN and self.TWILIO_FROM_NUMBER)

    @property
    def is_telegram_configured(self) -> bool:
        return bool(self.TELEGRAM_BOT_TOKEN)

    @property
    def is_smtp_configured(self) -> bool:
        return bool(self.SMTP_USER and self.SMTP_PASSWORD)

    @property
    def is_webhook_configured(self) -> bool:
        return bool(self.WEBHOOK_ALERT_URL)


settings = Settings()

