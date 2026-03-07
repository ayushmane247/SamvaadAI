"""
Scheme Loader Module (Owned by Ayush - AWS/Backend)

Responsibilities:
- Load scheme JSON files from S3
- Provide in-memory TTL cache
- Deterministic ordering guarantee
- Graceful failure handling with prototype scheme fallback
- Cold-start preload for Lambda

Architectural Guarantees:
- No scheme mutation
- Deterministic ordering (sorted by scheme_id)
- Same dataset version → same evaluation result
- No per-request S3 call (cache enforced)
- Fallback to embedded prototype schemes when S3 unavailable
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

try:
    _s3_client = boto3.client(
        "s3",
        region_name=config.AWS_REGION
    )
except Exception:
    _s3_client = None
    logger.warning("S3 client initialization failed — using prototype schemes")


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

    if _s3_client is None:
        raise RuntimeError("S3 client not available")

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
    # Test/Dev Environment → Prototype Schemes
    # -------------------------
    if config.is_test() or config.is_development():
        return _load_prototype_schemes()

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
        logger.error(f"Failed to load schemes from S3: {str(e)}")

        if _scheme_cache is not None:
            logger.warning("Returning stale cache due to S3 failure")
            return _scheme_cache

        # Final fallback: use prototype schemes
        logger.warning("S3 failed and no cache — falling back to prototype schemes")
        return _load_prototype_schemes()


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

if config.is_production():
    try:
        load_schemes()
        logger.info("Schemes preloaded at cold start.")
    except Exception as e:
        logger.warning(f"Cold-start preload failed: {str(e)}")


# =====================================
# Prototype Schemes — 5 Real Government Schemes
# =====================================

def _load_prototype_schemes() -> List[Dict]:
    """
    5 real Indian government schemes with eligibility rules,
    required documents, and official URLs.
    Used in dev/test mode and as S3 fallback.
    """
    schemes = [
        {
            "scheme_id": "PM_KISAN",
            "name": "PM Kisan Samman Nidhi",
            "eligibility_criteria": [
                {
                    "field": "farmer_status",
                    "operator": "equals",
                    "value": "true",
                    "explanation": "Must be a farmer"
                },
                {
                    "field": "occupation",
                    "operator": "equals",
                    "value": "farmer",
                    "explanation": "Occupation must be farming"
                }
            ],
            "logic": "OR",
            "benefit_summary": "₹6,000 per year in three installments directly to bank account for small and marginal farmers",
            "source_url": "https://pmkisan.gov.in/",
            "last_verified_date": "2026-03-01",
            "required_documents": [
                "Aadhaar Card",
                "Land ownership records",
                "Bank account details",
                "Mobile number linked to Aadhaar"
            ]
        },
        {
            "scheme_id": "AYUSHMAN_BHARAT",
            "name": "Ayushman Bharat - Pradhan Mantri Jan Arogya Yojana",
            "eligibility_criteria": [
                {
                    "field": "income",
                    "operator": "less_than",
                    "value": 500000,
                    "explanation": "Annual family income below ₹5 lakh"
                }
            ],
            "logic": "AND",
            "benefit_summary": "Health insurance cover of ₹5 lakh per family per year for secondary and tertiary hospitalization",
            "source_url": "https://pmjay.gov.in/",
            "last_verified_date": "2026-03-01",
            "required_documents": [
                "Aadhaar Card",
                "Ration Card / BPL certificate",
                "Income certificate",
                "Family ID / Family composition"
            ]
        },
        {
            "scheme_id": "PM_AWAS_YOJANA",
            "name": "Pradhan Mantri Awas Yojana",
            "eligibility_criteria": [
                {
                    "field": "income",
                    "operator": "less_than",
                    "value": 300000,
                    "explanation": "Annual household income below ₹3 lakh (EWS category)"
                }
            ],
            "logic": "AND",
            "benefit_summary": "Financial assistance up to ₹2.67 lakh for construction of pucca house with basic amenities",
            "source_url": "https://pmaymis.gov.in/",
            "last_verified_date": "2026-03-01",
            "required_documents": [
                "Aadhaar Card",
                "Income certificate",
                "Proof of land ownership or allotment letter",
                "Bank account details",
                "Affidavit of not owning a pucca house"
            ]
        },
        {
            "scheme_id": "NATIONAL_SCHOLARSHIP",
            "name": "National Scholarship Portal - Central Sector Scheme",
            "eligibility_criteria": [
                {
                    "field": "student_status",
                    "operator": "equals",
                    "value": "true",
                    "explanation": "Must be a student"
                },
                {
                    "field": "occupation",
                    "operator": "equals",
                    "value": "student",
                    "explanation": "Must be currently studying"
                }
            ],
            "logic": "OR",
            "benefit_summary": "Merit-based scholarship up to ₹20,000 per annum for higher education students from economically weaker families",
            "source_url": "https://scholarships.gov.in/",
            "last_verified_date": "2026-03-01",
            "required_documents": [
                "Aadhaar Card",
                "Mark sheets / certificates",
                "Income certificate of parents",
                "Bank account details",
                "Institution verification letter",
                "Caste certificate (if applicable)"
            ]
        },
        {
            "scheme_id": "PM_MUDRA_YOJANA",
            "name": "Pradhan Mantri Mudra Yojana",
            "eligibility_criteria": [
                {
                    "field": "occupation",
                    "operator": "in",
                    "value": ["business", "self-employed", "shopkeeper"],
                    "explanation": "Must be a non-farm small business owner or self-employed"
                }
            ],
            "logic": "AND",
            "benefit_summary": "Collateral-free loans up to ₹10 lakh for micro and small enterprises under Shishu, Kishore, and Tarun categories",
            "source_url": "https://www.mudra.org.in/",
            "last_verified_date": "2026-03-01",
            "required_documents": [
                "Aadhaar Card",
                "PAN Card",
                "Business plan / proposal",
                "Proof of business existence",
                "Bank statements (6 months)",
                "Passport-size photographs"
            ]
        }
    ]

    schemes.sort(key=lambda s: s["scheme_id"])
    return schemes