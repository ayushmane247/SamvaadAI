"""
LLM Service Configuration — Re-export Layer.

All canonical values live in core/config.py.
This module re-exports them under the names expected by llm_service modules,
preserving backward compatibility for fallback_templates.py and other consumers.
"""

from typing import Optional
import os

from core.config import config

# Bedrock settings (canonical source: core/config.py)
MODEL_ID: str = "anthropic.claude-3-haiku-20240307-v1:0"
REGION: str = "us-east-1"
TEMPERATURE: float = config.BEDROCK_TEMPERATURE
MAX_TOKENS: int = config.BEDROCK_MAX_TOKENS
TIMEOUT_SECONDS: int = config.BEDROCK_TIMEOUT_SECONDS

# Language settings (canonical source: core/config.py)
SUPPORTED_LANGUAGES: list = config.SUPPORTED_LANGUAGES
LANGUAGE_NAMES: dict = config.LANGUAGE_NAMES

# AWS Credentials (prefer IAM roles; only for local dev)
AWS_ACCESS_KEY_ID: Optional[str] = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY: Optional[str] = os.getenv("AWS_SECRET_ACCESS_KEY")

