"""
PENELOPE Backend - Request-ID & Observability Middleware
Extracts or assigns a unique UUID4 X-Request-ID to every incoming HTTP request,
attaches it to request state and response headers, and logs structured request timings.
"""

import time
import uuid
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("penelope.request")


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 1. Extract or generate Request-ID
        request_id = request.headers.get("X-Request-ID")
        if not request_id:
            request_id = str(uuid.uuid4())

        request.state.request_id = request_id
        start_time = time.perf_counter()

        # 2. Process request
        try:
            response: Response = await call_next(request)
        except Exception as exc:
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.error(f"[req_id={request_id}] {request.method} {request.url.path} - 500 ERROR in {duration_ms:.2f}ms: {exc}")
            raise exc

        # 3. Add header to response
        duration_ms = (time.perf_counter() - start_time) * 1000
        response.headers["X-Request-ID"] = request_id

        # 4. Structured log
        logger.info(f"[req_id={request_id}] {request.method} {request.url.path} - {response.status_code} in {duration_ms:.2f}ms")
        return response

