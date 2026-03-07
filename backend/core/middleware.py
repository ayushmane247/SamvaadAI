# core/middleware.py
"""
Middleware for request tracking, latency measurement, rate limiting,
and input sanitization.
"""

import re
import time
import uuid
from collections import defaultdict
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from core.logging_config import log_request
from core.config import config


class RequestTrackingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for tracking requests with structured logging.
    
    Responsibilities:
    - Generate unique request_id for each request
    - Measure request latency
    - Log structured request data
    - No business logic
    - No PII logging
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next):
        """
        Process request and track metrics.
        
        Args:
            request: Incoming request
            call_next: Next middleware/handler
            
        Returns:
            Response with tracking headers
        """
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Start timer
        start_time = time.time()
        
        # Process request
        response: Response = await call_next(request)
        
        # Calculate latency
        latency_ms = (time.time() - start_time) * 1000
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        
        # Log request if enabled
        if config.ENABLE_STRUCTURED_LOGGING:
            # Extract evaluation count from response if present
            evaluation_count = None
            error_type = None
            
            if response.status_code >= 400:
                error_type = f"HTTP_{response.status_code}"
            
            log_request(
                request_id=request_id,
                endpoint=request.url.path,
                status_code=response.status_code,
                latency_ms=latency_ms,
                evaluation_count=evaluation_count,
                error_type=error_type
            )
        
        return response


# ── Rate Limiting ─────────────────────────────────────────────────

# In-memory store: { ip: [timestamp, ...] }
_rate_store: dict[str, list[float]] = defaultdict(list)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Sliding-window rate limiter — configurable via config.py.

    Reads RATE_LIMIT_REQUESTS and RATE_LIMIT_WINDOW_SECONDS from config.
    Returns HTTP 429 when the limit is exceeded.
    Uses in-memory storage (suitable for single-process / Lambda).
    """

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        window_start = now - config.RATE_LIMIT_WINDOW_SECONDS

        # Prune old entries
        _rate_store[client_ip] = [
            ts for ts in _rate_store[client_ip] if ts > window_start
        ]

        if len(_rate_store[client_ip]) >= config.RATE_LIMIT_REQUESTS:
            return JSONResponse(
                status_code=429,
                content={"error": "Too many requests. Please try again later."},
            )

        _rate_store[client_ip].append(now)
        return await call_next(request)


# ── Prompt Injection Sanitizer ────────────────────────────────────

_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"system\s+prompt",
    r"developer\s+prompt",
    r"override\s+instructions",
    r"disregard\s+(all\s+)?prior",
    r"you\s+are\s+now\s+in\s+developer\s+mode",
    r"jailbreak",
    r"DAN\s+mode",
]

_INJECTION_RE = re.compile(
    "|".join(_INJECTION_PATTERNS), re.IGNORECASE
)


def sanitize_input(text: str) -> str:
    """
    Strip prompt-injection patterns from user input.

    Rules:
    - Removes known injection phrases
    - Strips excessive whitespace
    - Does NOT modify legitimate user information

    Args:
        text: Raw user input string.

    Returns:
        Sanitized string safe for LLM processing.
    """
    sanitized = _INJECTION_RE.sub("", text)
    # Collapse multiple spaces left by removal
    sanitized = re.sub(r"\s{2,}", " ", sanitized).strip()
    return sanitized

