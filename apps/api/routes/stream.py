"""
PENELOPE Backend - Server-Sent Events (SSE) Live Risk Stream (Part 4)
Subscribes to Redis 'risk.updates' pub/sub and pushes live map updates to web/mobile clients.
"""

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from apps.api.geospatial.events import stream_risk_sse

router = APIRouter(prefix="/stream", tags=["Live Stream"])


@router.get("/risk")
async def get_live_risk_stream():
    """
    Server-Sent Events (SSE) endpoint subscribing to Redis 'risk.updates' channel.
    Streams real-time flash-flood early warning and map updates to connected frontends.
    """
    return StreamingResponse(
        stream_risk_sse(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
