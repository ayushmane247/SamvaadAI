# core/config.py
"""
Centralized configuration management.
All environment-dependent values abstracted here.
"""

import os
from typing import Literal


class Config:
    """
    Application configuration.
    All environment variables centralized here.
    """
    
    # Environment
    APP_ENV: Literal["development", "production", "test"] = os.getenv("APP_ENV", "development")
    
    # API Configuration
    API_VERSION: str = "1.0.0"
    API_TITLE: str = "SamvaadAI API"
    API_ROOT_PATH: str = os.getenv("API_ROOT_PATH", "/prod")
    
    # AWS Configuration
    AWS_REGION: str = os.getenv("AWS_REGION", "ap-south-1")
    DYNAMODB_TABLE_NAME: str = os.getenv("DYNAMODB_TABLE_NAME", "samvaadai-sessions")
    S3_BUCKET_NAME: str = os.getenv("S3_BUCKET_NAME", "samvaadai-schemes")
    
    # Session Configuration
    SESSION_TTL_SECONDS: int = int(os.getenv("SESSION_TTL_SECONDS", "3600"))  # 1 hour
    
    # Performance Thresholds (from requirements.md)
    API_LATENCY_THRESHOLD_MS: int = 500  # p95 < 500ms
    EVALUATION_LATENCY_THRESHOLD_MS: int = 2000  # < 2 seconds
    
    # Feature Toggles
    ENABLE_STRUCTURED_LOGGING: bool = os.getenv("ENABLE_STRUCTURED_LOGGING", "true").lower() == "true"
    ENABLE_LATENCY_TRACKING: bool = os.getenv("ENABLE_LATENCY_TRACKING", "true").lower() == "true"
    
    # Scheme Caching
    SCHEME_CACHE_ENABLED: bool = os.getenv("SCHEME_CACHE_ENABLED", "true").lower() == "true"
    SCHEME_CACHE_TTL_SECONDS: int = int(os.getenv("SCHEME_CACHE_TTL_SECONDS", "300"))  # 5 minutes
    
    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production environment"""
        return cls.APP_ENV == "production"
    
    @classmethod
    def is_development(cls) -> bool:
        """Check if running in development environment"""
        return cls.APP_ENV == "development"
    
    @classmethod
    def is_test(cls) -> bool:
        """Check if running in test environment"""
        return cls.APP_ENV == "test"


# Singleton instance
config = Config()
