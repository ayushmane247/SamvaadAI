"""
Scheme Loader Module (Owned by Ayush - AWS/Backend)

Responsibilities:
- Load scheme JSON files from S3
- Provide in-memory TTL cache
- Deterministic ordering guarantee
- Graceful failure handling
- Cold-start preload for Lambda

Architectural Guarantees:
- No scheme mutation
- Deterministic ordering (sorted by scheme_id)
- Same dataset version → same evaluation result
- No per-request S3 call (cache enforced)
"""

from typing import List, Dict, Optional
from datetime import datetime, timezone
import json
import boto3
from botocore.exceptions import ClientError

from core.config import config
from core.logging_config import logger


# =====================================
# AWS S3 Client (Module Level - Lambda Reuse)
# =====================================

_s3_client = boto3.client(
    "s3",
    region_name=config.AWS_REGION
)


# =====================================
# In-Memory Cache
# =====================================

_scheme_cache: Optional[List[Dict]] = None
_cache_timestamp: Optional[datetime] = None


# =====================================
# Configuration Defaults
# =====================================

SCHEME_PREFIX = "maharashtra/"  # Hackathon scope: Maharashtra only


# =====================================
# Cache Validation
# =====================================

def _is_cache_valid() -> bool:
    if not config.SCHEME_CACHE_ENABLED:
        return False

    if _scheme_cache is None or _cache_timestamp is None:
        return False

    cache_age = (
        datetime.now(timezone.utc) - _cache_timestamp
    ).total_seconds()

    return cache_age < config.SCHEME_CACHE_TTL_SECONDS


# =====================================
# Scheme Validation
# =====================================

def _validate_scheme(scheme: Dict) -> bool:
    required_fields = {
        "scheme_id",
        "name",
        "eligibility_criteria",
        "logic",
        "benefit_summary",
        "source_url",
        "last_verified_date",
    }

    missing = required_fields - scheme.keys()
    if missing:
        logger.error(
            f"Scheme {scheme.get('scheme_id')} missing fields: {missing}"
        )
        return False

    if not isinstance(scheme["eligibility_criteria"], list):
        logger.error(
            f"Scheme {scheme.get('scheme_id')} eligibility_criteria must be list"
        )
        return False

    return True


# =====================================
# S3 Loading Logic
# =====================================

def _load_schemes_from_s3() -> List[Dict]:
    logger.info("Loading schemes from S3...")

    schemes: List[Dict] = []

    try:
        paginator = _s3_client.get_paginator("list_objects_v2")
        page_iterator = paginator.paginate(
            Bucket=config.S3_BUCKET_NAME,
            Prefix="maharashtra/"
        )

        for page in page_iterator:
            for obj in page.get("Contents", []):
                key = obj["Key"]

                # Skip folder objects
                if key.endswith("/") or not key.endswith(".json"):
                    continue

                try:
                    file_obj = _s3_client.get_object(
                        Bucket=config.S3_BUCKET_NAME,
                        Key=key
                    )

                    body = file_obj["Body"].read()
                    scheme = json.loads(body)

                    if _validate_scheme(scheme):
                        schemes.append(scheme)

                except Exception as e:
                    logger.error(
                        f"Skipping malformed scheme {key}: {str(e)}"
                    )
                    continue

        # Deterministic ordering guarantee
        schemes.sort(key=lambda s: s.get("scheme_id", ""))

        logger.info(
            f"Loaded {len(schemes)} schemes from bucket {config.S3_BUCKET_NAME}"
        )

        return schemes

    except ClientError as e:
        logger.error(f"S3 access failed: {str(e)}")
        raise


# =====================================
# Public Loader
# =====================================

def load_schemes() -> List[Dict]:
    global _scheme_cache, _cache_timestamp

    # -------------------------
    # Test Environment Bypass
    # -------------------------
    if config.is_test():
        return _load_mock_schemes()

    # -------------------------
    # Cache Check
    # -------------------------
    if _is_cache_valid():
        logger.debug("Returning schemes from cache")
        return _scheme_cache

    # -------------------------
    # Load From S3
    # -------------------------
    try:
        schemes = _load_schemes_from_s3()

        _scheme_cache = schemes
        _cache_timestamp = datetime.now(timezone.utc)

        return schemes

    except Exception as e:
        logger.error(f"Failed to load schemes: {str(e)}")

        if _scheme_cache is not None:
            logger.warning("Returning stale cache due to S3 failure")
            return _scheme_cache

        raise


# =====================================
# Cache Invalidation (Manual Trigger)
# =====================================

def invalidate_cache() -> None:
    global _scheme_cache, _cache_timestamp
    _scheme_cache = None
    _cache_timestamp = None
    logger.info("Scheme cache invalidated")


# =====================================
# Cold-Start Preload (Lambda Optimization)
# =====================================

if not config.is_test():
    try:
        load_schemes()
        logger.info("Schemes preloaded at cold start.")
    except Exception as e:
        logger.warning(f"Cold-start preload failed: {str(e)}")


# =====================================
# Mock Schemes (Test Environment Only)
# =====================================

def _load_mock_schemes() -> List[Dict]:
    schemes = [
        {
            "scheme_id": "FARMER_SUPPORT",
            "name": "Farmer Support Scheme",
            "eligibility_criteria": [
                {
                    "field": "occupation",
                    "operator": "equals",
                    "value": "farmer",
                    "explanation": "Must be farmer"
                }
            ],
            "logic": "AND",
            "benefit_summary": "Financial support for farmers",
            "source_url": "https://example.com/farmer-support",
            "last_verified_date": "2025-02-15"
        },
        {
            "scheme_id": "LOW_INCOME_SUPPORT",
            "name": "Low Income Support Scheme",
            "eligibility_criteria": [
                {
                    "field": "income",
                    "operator": "less_than",
                    "value": 100000,
                    "explanation": "Annual income < 1 lakh"
                }
            ],
            "logic": "AND",
            "benefit_summary": "Financial assistance for low income families",
            "source_url": "https://example.com/low-income-support",
            "last_verified_date": "2025-02-15"
        },
        {
    "scheme_id": "YOUTH_EMPLOYMENT",
    "name": "Youth Employment Scheme",
    "eligibility_criteria": [
        {
            "field": "age",
            "operator": "between",
            "value": [18, 35],
            "explanation": "Age between 18 and 35"
        },
        {
            "field": "state",
            "operator": "equals",
            "value": "Maharashtra",
            "explanation": "Must be from Maharashtra"
        }
    ],
    "logic": "AND",
    "benefit_summary": "Employment assistance for youth",
    "source_url": "https://example.com/youth-employment",
    "last_verified_date": "2025-02-15"
}
    ]

    schemes.sort(key=lambda s: s["scheme_id"])
    return schemes