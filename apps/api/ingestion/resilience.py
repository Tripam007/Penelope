"""
PENELOPE Backend - Resilience Utilities
Circuit breaker, Redis/in-memory cache, exponential backoff, and ingest health tracker.
"""

import time
import random
import asyncio
import logging
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timedelta

logger = logging.getLogger("penelope.ingestion.resilience")


# ============================================================================
# 1. PER-PROVIDER CIRCUIT BREAKER
# ============================================================================
class CircuitBreakerOpenException(Exception):
    pass


class CircuitBreaker:
    """
    Three-state circuit breaker:
    - CLOSED: Normal operation, passing requests.
    - OPEN: Failing fast after consecutive failures, protecting downstream provider.
    - HALF_OPEN: Allowing trial probes to test provider recovery.
    """
    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_time_sec: float = 60.0,
        half_open_max_probes: int = 2
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_time_sec = recovery_time_sec
        self.half_open_max_probes = half_open_max_probes

        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.consecutive_failures = 0
        self.last_failure_time = 0.0
        self.half_open_probes = 0

    def can_execute(self) -> bool:
        now = time.time()
        if self.state == "CLOSED":
            return True

        if self.state == "OPEN":
            if now - self.last_failure_time >= self.recovery_time_sec:
                logger.info(f"CircuitBreaker [{self.name}]: Transitioning from OPEN to HALF_OPEN")
                self.state = "HALF_OPEN"
                self.half_open_probes = 0
                return True
            return False

        if self.state == "HALF_OPEN":
            return self.half_open_probes < self.half_open_max_probes

        return True

    def record_success(self):
        if self.state in ("HALF_OPEN", "OPEN"):
            logger.info(f"CircuitBreaker [{self.name}]: Provider recovered, resetting to CLOSED")
        self.consecutive_failures = 0
        self.state = "CLOSED"
        self.half_open_probes = 0

    def record_failure(self, error: Optional[Exception] = None):
        self.consecutive_failures += 1
        self.last_failure_time = time.time()
        logger.warning(
            f"CircuitBreaker [{self.name}]: Recorded failure #{self.consecutive_failures} (State: {self.state}) - {error}"
        )

        if self.state == "HALF_OPEN" or self.consecutive_failures >= self.failure_threshold:
            self.state = "OPEN"
            logger.error(
                f"CircuitBreaker [{self.name}]: TRIP! State is now OPEN for {self.recovery_time_sec}s"
            )


# Global registry of circuit breakers
_circuit_breakers: Dict[str, CircuitBreaker] = {}


def get_circuit_breaker(name: str, failure_threshold: int = 4, recovery_time_sec: float = 45.0) -> CircuitBreaker:
    if name not in _circuit_breakers:
        _circuit_breakers[name] = CircuitBreaker(
            name, failure_threshold=failure_threshold, recovery_time_sec=recovery_time_sec
        )
    return _circuit_breakers[name]


# ============================================================================
# 2. EXPONENTIAL BACKOFF WITH JITTER
# ============================================================================
async def retry_with_backoff(
    func: Callable,
    *args,
    max_retries: int = 3,
    base_delay: float = 0.5,
    max_delay: float = 6.0,
    circuit_breaker: Optional[CircuitBreaker] = None,
    **kwargs
) -> Any:
    """
    Executes an async function with exponential backoff, jitter, and optional circuit breaker.
    """
    if circuit_breaker and not circuit_breaker.can_execute():
        raise CircuitBreakerOpenException(f"Circuit breaker '{circuit_breaker.name}' is OPEN.")

    last_exc = None
    for attempt in range(max_retries):
        try:
            if circuit_breaker and circuit_breaker.state == "HALF_OPEN":
                circuit_breaker.half_open_probes += 1

            result = await func(*args, **kwargs)
            if circuit_breaker:
                circuit_breaker.record_success()
            return result
        except Exception as e:
            last_exc = e
            if circuit_breaker:
                circuit_breaker.record_failure(e)

            if attempt == max_retries - 1:
                break

            delay = min(max_delay, base_delay * (2 ** attempt)) + random.uniform(0.05, 0.25)
            logger.debug(f"Retrying {func.__name__} in {delay:.2f}s (attempt {attempt + 1}/{max_retries})")
            await asyncio.sleep(delay)

    raise last_exc


# ============================================================================
# 3. HYBRID CACHE (REDIS WITH IN-MEMORY FALLBACK)
# ============================================================================
class HybridCache:
    """
    Provides caching backed by Redis if available, with transparent in-memory fallback.
    """
    def __init__(self):
        self._memory_cache: Dict[str, Dict[str, Any]] = {}
        self._redis_client = None
        self._tried_redis = False

    def _get_redis(self):
        if not self._tried_redis:
            self._tried_redis = True
            try:
                import redis
                from apps.api.config import settings
                client = redis.from_url(settings.REDIS_URL, decode_responses=True, socket_timeout=1.0)
                client.ping()
                self._redis_client = client
                logger.info("Connected to Redis cache.")
            except Exception as e:
                logger.info(f"Redis not connected ({e}), using thread-safe in-memory cache.")
                self._redis_client = None
        return self._redis_client

    def get(self, key: str) -> Optional[Any]:
        r = self._get_redis()
        if r:
            try:
                val = r.get(key)
                if val is not None:
                    import json
                    return json.loads(val)
            except Exception:
                pass

        # Memory fallback
        item = self._memory_cache.get(key)
        if item:
            if time.time() < item["expires_at"]:
                return item["value"]
            else:
                del self._memory_cache[key]
        return None

    def set(self, key: str, value: Any, ttl_sec: int = 300):
        r = self._get_redis()
        if r:
            try:
                import json
                r.setex(key, ttl_sec, json.dumps(value))
                return
            except Exception:
                pass

        self._memory_cache[key] = {
            "value": value,
            "expires_at": time.time() + ttl_sec
        }


cache = HybridCache()


# ============================================================================
# 4. INGEST HEALTH & TELEMETRY TRACKER
# ============================================================================
class IngestHealthTracker:
    """
    Tracks the last successful run, status, and staleness of each ingestion source.
    """
    def __init__(self):
        self._state: Dict[str, Dict[str, Any]] = {
            "weather": {
                "last_success": None,
                "status": "pending",
                "records_ingested": 0,
                "error": None,
                "threshold_min": 60,  # Stale if > 60m
            },
            "glofas": {
                "last_success": None,
                "status": "pending",
                "records_ingested": 0,
                "error": None,
                "threshold_min": 360,  # Stale if > 6h
            },
            "sensor": {
                "last_success": None,
                "status": "pending",
                "records_ingested": 0,
                "error": None,
                "threshold_min": 30,  # Stale if > 30m
            },
            "terrain": {
                "last_success": None,
                "status": "pending",
                "records_ingested": 0,
                "error": None,
                "threshold_min": 1440 * 7,  # Stale if > 7 days (static DEM)
            },
        }

    def record_run(self, source: str, count: int, error: Optional[str] = None):
        if source not in self._state:
            self._state[source] = {"threshold_min": 60}

        entry = self._state[source]
        if error:
            entry["status"] = "error"
            entry["error"] = str(error)
        else:
            entry["status"] = "fresh"
            entry["last_success"] = datetime.utcnow().isoformat() + "Z"
            entry["records_ingested"] = entry.get("records_ingested", 0) + count
            entry["error"] = None

    def get_summary(self) -> Dict[str, Any]:
        now = datetime.utcnow()
        summary = {}
        for src, data in self._state.items():
            last_dt = None
            is_stale = True
            if data["last_success"]:
                try:
                    ts_clean = data["last_success"].replace("Z", "")
                    last_dt = datetime.fromisoformat(ts_clean)
                    age_min = (now - last_dt).total_seconds() / 60.0
                    is_stale = age_min > data["threshold_min"]
                except Exception:
                    is_stale = False

            summary[src] = {
                "status": "stale" if (is_stale and data["last_success"]) else data["status"],
                "last_success": data["last_success"],
                "records_ingested": data.get("records_ingested", 0),
                "is_stale": is_stale,
                "error": data.get("error"),
                "staleness_threshold_min": data["threshold_min"],
            }
        return summary


ingest_health = IngestHealthTracker()
