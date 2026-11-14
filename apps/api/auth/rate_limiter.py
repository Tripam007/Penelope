"""
PENELOPE Backend - Rate Limiting & Protection
Provides IP-based sliding window rate limiting for public and auth endpoints,
with slowapi compatibility and HTTP 429 Too Many Requests response handling.
"""

import time
from typing import Dict, List, Callable
from fastapi import Request, HTTPException, status
from collections import defaultdict

# In-memory IP request history: ip -> list of timestamps
_request_history: Dict[str, List[float]] = defaultdict(list)


class RateLimiter:
    def __init__(self, max_requests: int = 60, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    def __call__(self, request: Request):
        client_ip = request.client.host if request.client else "127.0.0.1"
        now = time.time()
        window_start = now - self.window_seconds

        # Prune older entries
        history = [ts for ts in _request_history[client_ip] if ts > window_start]
        if len(history) >= self.max_requests:
            retry_after = int(self.window_seconds - (now - history[0])) + 1
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later.",
                headers={"Retry-After": str(max(1, retry_after))}
            )

        history.append(now)
        _request_history[client_ip] = history
        return True


# Predefined rate limiters
auth_rate_limit = RateLimiter(max_requests=20, window_seconds=60)
api_rate_limit = RateLimiter(max_requests=120, window_seconds=60)

