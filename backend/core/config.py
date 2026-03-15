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
    def validate(self):
        """
        Validate configuration values.
        In test mode this is skipped.
        """
        if self.APP_ENV == "test":
            return True
    
    # Environment
    APP_ENV: Literal["development", "production", "test"] = os.getenv("APP_ENV", "development")
    
    # API Configuration
    API_VERSION: str = "1.0.0"
    API_TITLE: str = "SamvaadAI API"
    API_ROOT_PATH: str = os.getenv("API_ROOT_PATH", "/prod")
    
    # AWS Configuration
    AWS_REGION: str = os.getenv("AWS_REGION", "ap-south-1")
    DYNAMODB_TABLE_NAME: str = os.getenv("DYNAMODB_TABLE_NAME", "samvaadai-sessions")
    S3_BUCKET_NAME: str = os.getenv("S3_BUCKET_NAME", "samvaadai-schemes-prod")
    
    # Session Configuration
    SESSION_TTL_SECONDS: int = int(os.getenv("SESSION_TTL_SECONDS", "3600"))  # 1 hour
    
    # Performance Thresholds (from requirements.md)
    API_LATENCY_THRESHOLD_MS: int = 500  # p95 < 500ms
    EVALUATION_LATENCY_THRESHOLD_MS: int = 2000  # < 2 seconds
    
    # Feature Toggles
    ENABLE_STRUCTURED_LOGGING: bool = os.getenv("ENABLE_STRUCTURED_LOGGING", "true").lower() == "true"
    ENABLE_LATENCY_TRACKING: bool = os.getenv("ENABLE_LATENCY_TRACKING", "true").lower() == "true"
    
    # Adaptive Questioning Configuration (Phase 2)
    ADAPTIVE_QUESTIONING_ENABLED: bool = os.getenv("ADAPTIVE_QUESTIONING_ENABLED", "true").lower() == "true"
    ADAPTIVE_QUESTIONING_CACHE_ENABLED: bool = os.getenv("ADAPTIVE_QUESTIONING_CACHE_ENABLED", "true").lower() == "true"
    ADAPTIVE_QUESTIONING_PERFORMANCE_THRESHOLD_MS: int = int(os.getenv("ADAPTIVE_QUESTIONING_PERFORMANCE_THRESHOLD_MS", "100"))
    
    # Simulation-based Adaptive Questioning (New Implementation)
    SIMULATION_BASED_QUESTIONING_ENABLED: bool = os.getenv("SIMULATION_BASED_QUESTIONING_ENABLED", "true").lower() == "true"
    
    # Scheme Explainability Engine
    SCHEME_EXPLAINABILITY_ENABLED: bool = os.getenv("SCHEME_EXPLAINABILITY_ENABLED", "true").lower() == "true"
    
    # High-value scheme detection keywords
    HIGH_VALUE_KEYWORDS: list = ["lakh", "₹", "insurance", "subsidy", "pension"]
    
    ALLOWED_ORIGINS: str = os.getenv("ALLOWED_ORIGINS", "*")
    
    # Scheme Caching
    SCHEME_CACHE_ENABLED: bool = os.getenv("SCHEME_CACHE_ENABLED", "true").lower() == "true"
    SCHEME_CACHE_TTL_SECONDS: int = int(os.getenv("SCHEME_CACHE_TTL_SECONDS", "300"))  # 5 minutes

    # Bedrock / LLM Configuration
    BEDROCK_ENABLED: bool = os.getenv("BEDROCK_ENABLED", "true").lower() == "true"
    BEDROCK_MODEL_ID: str = os.getenv("BEDROCK_MODEL_ID", "global.amazon.nova-2-lite-v1:0")
    BEDROCK_TEMPERATURE: float = 0.2  # Deterministic output
    BEDROCK_MAX_TOKENS: int = 1024
    BEDROCK_TIMEOUT_SECONDS: int = int(os.getenv("BEDROCK_TIMEOUT_SECONDS", "3"))  # 3s spec limit
    LLM_ENHANCEMENT_THRESHOLD: int = int(os.getenv("LLM_ENHANCEMENT_THRESHOLD", "300"))  # Increased from 150

    # Language Support
    SUPPORTED_LANGUAGES: list = ["en", "hi", "mr"]
    LANGUAGE_NAMES: dict = {
        "en": "English",
        "hi": "Hindi",
        "mr": "Marathi",
    }

    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    RATE_LIMIT_WINDOW_SECONDS: int = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))
    
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
