"""
PENELOPE Geospatial Risk Engine - Real-Time Risk Streaming & Event Bus
Subscribes to Redis pub/sub channel 'risk.updates' and bridges to Server-Sent Events (SSE),
with automatic graceful degradation to an in-memory event bus when Redis is offline.
"""

import json
import asyncio
import logging
from datetime import datetime
from typing import AsyncGenerator, Dict, Any, Set
from apps.api.config import settings

logger = logging.getLogger("penelope.geospatial.events")

REDIS_RISK_CHANNEL = "risk.updates"


class RiskEventBus:
    """
    Hybrid event bus: publishes to Redis 'risk.updates' and multicasts to
    local async client queues for Server-Sent Events (SSE).
    """
    def __init__(self):
        self._listeners: Set[asyncio.Queue] = set()
        self._redis_client = None
        self._redis_pubsub = None
        self._redis_listener_task = None
        self._redis_connected = False

    def _get_redis(self):
        if self._redis_client is None and not self._redis_connected:
            try:
                import redis
                client = redis.from_url(settings.REDIS_URL, decode_responses=True, socket_timeout=1.0)
                client.ping()
                self._redis_client = client
                self._redis_connected = True
                logger.info("RiskEventBus connected to Redis pub/sub.")
            except Exception as e:
                logger.debug(f"Redis unavailable for pub/sub ({e}); using memory event bus.")
                self._redis_client = None
        return self._redis_client

    def register_listener(self) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue(maxsize=100)
        self._listeners.add(q)
        return q

    def unregister_listener(self, q: asyncio.Queue):
        if q in self._listeners:
            self._listeners.remove(q)

    def publish(self, payload: Dict[str, Any]):
        """
        Publishes a risk update payload to both Redis 'risk.updates'
        and all active in-memory SSE listeners.
        """
        if "timestamp" not in payload:
            payload["timestamp"] = datetime.utcnow().isoformat() + "Z"

        # 1. Publish to Redis if available
        r = self._get_redis()
        if r:
            try:
                r.publish(REDIS_RISK_CHANNEL, json.dumps(payload))
            except Exception as e:
                logger.warning(f"Error publishing to Redis {REDIS_RISK_CHANNEL}: {e}")

        # 2. Multicast to active local SSE queues
        dead_queues = []
        for q in self._listeners:
            try:
                q.put_nowait(payload)
            except asyncio.QueueFull:
                dead_queues.append(q)

        for dq in dead_queues:
            self._listeners.discard(dq)


risk_event_bus = RiskEventBus()


async def stream_risk_sse() -> AsyncGenerator[str, None]:
    """
    Async generator yielding Server-Sent Events for GET /v1/stream/risk.
    Format:
        event: risk_update
        data: {...}
    """
    q = risk_event_bus.register_listener()

    # Initial snapshot greeting
    initial_event = {
        "type": "INITIAL_SNAPSHOT",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "message": "Connected to PENELOPE live geospatial risk stream.",
        "channel": REDIS_RISK_CHANNEL
    }
    yield f"event: connection\ndata: {json.dumps(initial_event)}\n\n"

    try:
        while True:
            try:
                # Wait for next published event with 15s timeout for keep-alive ping
                event_data = await asyncio.wait_for(q.get(), timeout=15.0)
                event_type = event_data.get("type", "risk_update")
                yield f"event: {event_type}\ndata: {json.dumps(event_data)}\n\n"
            except asyncio.TimeoutError:
                # Send SSE keep-alive heartbeat ping
                ping = {"type": "ping", "timestamp": datetime.utcnow().isoformat() + "Z"}
                yield f": keep-alive\ndata: {json.dumps(ping)}\n\n"
    finally:
        risk_event_bus.unregister_listener(q)
