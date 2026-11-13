"""
PENELOPE Backend - Database Connection & Session Management
SQLAlchemy 2.0 Engine with automatic PostgreSQL / SQLite compatibility.
"""

import os
import logging
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
from apps.api.config import settings

logger = logging.getLogger("penelope.database")


class Base(DeclarativeBase):
    pass


def get_active_sync_db_url() -> str:
    if os.getenv("USE_POSTGRES") == "true" or os.getenv("DOCKER_CONTAINER") == "true":
        return settings.DATABASE_SYNC_URL
    return "sqlite:///./penelope.db"


active_db_url = get_active_sync_db_url()
engine = create_engine(
    active_db_url,
    echo=False,
    connect_args={"check_same_thread": False} if "sqlite" in active_db_url else {}
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db():
    from apps.api import models  # Ensure all models are registered
    Base.metadata.create_all(bind=engine)
    logger.info(f"Database schema initialized ({active_db_url}).")
