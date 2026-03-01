# core/logging_config.py
"""
Centralized structured logging configuration.
Machine-readable JSON logs with no PII leakage.
"""

import logging
import json
import sys
from datetime import datetime, UTC
from typing import Any, Dict, Optional
from core.config import config



class StructuredFormatter(logging.Formatter):
    """
    JSON formatter for structured logging.
    Outputs machine-readable logs.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON.
        
        Args:
            record: Log record
            
        Returns:
            JSON string
        """
        log_data: Dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Add extra fields if present
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        
        if hasattr(record, "endpoint"):
            log_data["endpoint"] = record.endpoint
        
        if hasattr(record, "status_code"):
            log_data["status_code"] = record.status_code
        
        if hasattr(record, "latency_ms"):
            log_data["latency_ms"] = record.latency_ms
        
        if hasattr(record, "evaluation_count"):
            log_data["evaluation_count"] = record.evaluation_count
        
        if hasattr(record, "error_type"):
            log_data["error_type"] = record.error_type
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)


def setup_logging() -> logging.Logger:
    """
    Configure structured logging for the application.
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger("samvaadai")
    logger.setLevel(logging.INFO if config.is_production() else logging.DEBUG)
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    
    # Use structured formatter if enabled
    if config.ENABLE_STRUCTURED_LOGGING:
        handler.setFormatter(StructuredFormatter())
    else:
        # Simple format for development
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
        )
    
    logger.addHandler(handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger


# Global logger instance
logger = setup_logging()


def log_request(
    request_id: str,
    endpoint: str,
    status_code: int,
    latency_ms: float,
    evaluation_count: Optional[int] = None,
    error_type: Optional[str] = None
) -> None:
    """
    Log API request with structured data.
    
    Args:
        request_id: Unique request identifier
        endpoint: API endpoint path
        status_code: HTTP status code
        latency_ms: Request latency in milliseconds
        evaluation_count: Number of schemes evaluated (if applicable)
        error_type: Error type if request failed
    """
    extra = {
        "request_id": request_id,
        "endpoint": endpoint,
        "status_code": status_code,
        "latency_ms": round(latency_ms, 2),
    }
    
    if evaluation_count is not None:
        extra["evaluation_count"] = evaluation_count
    
    if error_type:
        extra["error_type"] = error_type
    
    if status_code >= 500:
        logger.error("Request failed", extra=extra)
    elif status_code >= 400:
        logger.warning("Request error", extra=extra)
    else:
        logger.info("Request completed", extra=extra)
