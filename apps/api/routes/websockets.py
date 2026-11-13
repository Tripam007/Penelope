"""
PENELOPE Backend - WebSockets & SSE Real-Time Streaming
Broadcasts live sensor telemetry and flood risk alerts to connected clients.
"""

import json
import asyncio
import logging
from typing import List
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from apps.api.ingestion.scheduler import latest_broadcast_events

logger = logging.getLogger("penelope.websockets")
router = APIRouter(tags=["Realtime"])


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket client connected. Total clients: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket client disconnected. Total clients: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        text = json.dumps(message)
        for connection in list(self.active_connections):
            try:
                await connection.send_text(text)
            except Exception:
                self.disconnect(connection)


manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    last_event_idx = len(latest_broadcast_events)

    try:
        # Send initial welcome message
        await websocket.send_json({
            "type": "CONNECTION_ESTABLISHED",
            "message": "Connected to PENELOPE real-time flash-flood early-warning telemetry stream."
        })

        while True:
            # Check for new events
            if len(latest_broadcast_events) > last_event_idx:
                new_events = latest_broadcast_events[last_event_idx:]
                last_event_idx = len(latest_broadcast_events)
                for ev in new_events:
                    await websocket.send_json(ev)

            # Keep connection alive with small sleep
            await asyncio.sleep(1.0)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


@router.get("/events/sse")
async def sse_event_stream():
    """
    Server-Sent Events (SSE) alternative for lightweight web & mobile clients.
    """
    async def event_generator():
        last_idx = len(latest_broadcast_events)
        while True:
            if len(latest_broadcast_events) > last_idx:
                new_events = latest_broadcast_events[last_idx:]
                last_idx = len(latest_broadcast_events)
                for ev in new_events:
                    yield f"data: {json.dumps(ev)}\n\n"
            await asyncio.sleep(1.5)

    return StreamingResponse(event_generator(), media_type="text/event-stream")
