"""Rate limiting middleware."""
from __future__ import annotations

import logging
import time
from collections import defaultdict
from typing import Callable

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings

logger = logging.getLogger(__name__)

# In-memory rate limit store (use Redis in production)
_rate_limit_store: dict[str, list[float]] = defaultdict(list)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware using sliding window."""
    
    async def dispatch(self, request: Request, call_next: Callable):
        if not settings.rate_limit_enabled:
            return await call_next(request)
        
        # Skip rate limiting for health checks, static files, SSE streams, and API endpoints
        if (request.url.path in ["/health", "/healthz", "/favicon.ico"] or 
            request.url.path.startswith("/static") or
            request.url.path.startswith("/stream") or
            request.url.path.startswith("/events") or
            request.url.path.startswith("/logs/stream") or
            request.url.path.startswith("/advisor") or
            request.url.path.startswith("/charts/mini") or
            request.url.path.startswith("/silverback/streaming-demo") or
            request.url.path.startswith("/api/")):
            return await call_next(request)
        
        # Skip rate limiting for localhost in development
        client_ip = request.client.host if request.client else "unknown"
        if client_ip in ["127.0.0.1", "localhost", "::1"] and settings.debug:
            return await call_next(request)
        
        # Clean old entries (older than 1 minute)
        now = time.time()
        window_start = now - 60
        
        if client_ip in _rate_limit_store:
            _rate_limit_store[client_ip] = [
                timestamp for timestamp in _rate_limit_store[client_ip]
                if timestamp > window_start
            ]
        
        # Check rate limit
        request_count = len(_rate_limit_store[client_ip])
        
        if request_count >= settings.rate_limit_per_minute:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "rate_limit_exceeded",
                    "detail": f"Rate limit exceeded. Maximum {settings.rate_limit_per_minute} requests per minute.",
                    "retry_after": 60,
                },
                headers={"Retry-After": "60"},
            )
        
        # Add current request timestamp
        _rate_limit_store[client_ip].append(now)
        
        return await call_next(request)

