# backend\api\main.py
"""
FastAPI Application Entry Point.

Responsibilities:
- Application initialization
- Middleware registration
- Router registration
- Global exception handling
- CORS configuration
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from mangum import Mangum

from api.routes import router
from core.middleware import RequestTrackingMiddleware, RateLimitMiddleware
from core.config import config
from core.logging_config import logger
from llm_service.bedrock_client import is_available as bedrock_is_available

config.validate()

root_path = "/prod" if config.is_production() else ""


# Initialize FastAPI app
app = FastAPI(
    title=config.API_TITLE,
    version=config.API_VERSION,
    root_path=root_path
)

class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """Enforce maximum request body size."""
    
    MAX_SIZE = 10 * 1024  # 10KB
    
    async def dispatch(self, request: Request, call_next):
        if request.method in ["POST", "PUT", "PATCH"]:
            content_length = request.headers.get("content-length")
            if content_length and int(content_length) > self.MAX_SIZE:
                raise HTTPException(
                    status_code=413,
                    detail=f"Request body too large (max {self.MAX_SIZE} bytes)"
                )
        
        response = await call_next(request)
        return response

app.add_middleware(RequestSizeLimitMiddleware)

# Middleware (order matters: outermost runs first)
# 1. Request tracking (outermost — adds request ID + logging)
app.add_middleware(RequestTrackingMiddleware)

# 2. Rate limiting (before CORS — blocks excess traffic early)
app.add_middleware(RateLimitMiddleware)

# 3. CORS (innermost of custom middleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS.split(",") if config.is_production() else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Single canonical router
app.include_router(router)


@app.get("/health")
def health():
    """
    Health check endpoint.
    
    Returns:
        Status indicator with service health details
    """
    health_status = {
        "status": "ok",
        "version": config.API_VERSION,
        "mode": "hybrid" if config.BEDROCK_ENABLED else "deterministic",
        "bedrock_available": bedrock_is_available() if config.BEDROCK_ENABLED else None,
    }
    return health_status


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler.
    
    Ensures:
    - No PII leakage
    - No stack traces in production
    - Structured error logging
    
    Args:
        request: Request object
        exc: Exception raised
        
    Returns:
        Safe error response
    """
    request_id = getattr(request.state, "request_id", "unknown")
    
    logger.error(
        f"Unhandled exception: {str(exc)}",
        extra={"request_id": request_id, "error_type": type(exc).__name__},
        exc_info=True
    )
    
    # Safe error response (no internal details)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "request_id": request_id
        },
    )


# Lambda handler
handler = Mangum(app)