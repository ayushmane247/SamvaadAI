# core/middleware.py
"""
Middleware for request tracking, latency measurement, and structured logging.
"""

import time
import uuid
from fastapi import Request, Response
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
