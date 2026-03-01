# Scheme Loader - (Ayush owns this)
# Loads scheme data from S3

"""
Scheme Loader Module

Responsibilities:
- Load scheme data from S3 (future)
- Provide in-memory caching
- Handle scheme loading failures gracefully

Current Implementation: Mock data for MVP
Future Implementation: S3 integration with versioning

Caching Strategy:
- In-memory cache with configurable TTL
- Cold-start: Load schemes on first request
- Cache invalidation: TTL-based (default 5 minutes)
- Failure mode: Return cached data if S3 unavailable

Expected Behavior for S3 Integration:
1. On first load: Fetch from S3, cache in memory
2. On subsequent loads: Return from cache if not expired
3. On cache expiry: Refresh from S3, update cache
4. On S3 failure: Return stale cache with warning log
5. On malformed JSON: Skip invalid schemes, log error

Deterministic Guarantee:
- Same scheme data version produces same evaluation results
- Scheme ordering is deterministic (sorted by scheme_id)
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
from core.config import config
from core.logging_config import logger


# In-memory cache
_scheme_cache: Optional[List[Dict]] = None
_cache_timestamp: Optional[datetime] = None


def _is_cache_valid() -> bool:
    """
    Check if cache is valid based on TTL.
    
    Returns:
        True if cache is valid, False otherwise
    """
    if not config.SCHEME_CACHE_ENABLED:
        return False
    
    if _scheme_cache is None or _cache_timestamp is None:
        return False
    
    cache_age = (datetime.now(UTC) - _cache_timestamp).total_seconds()
    return cache_age < config.SCHEME_CACHE_TTL_SECONDS


def _load_schemes_from_source() -> List[Dict]:
    """
    Load schemes from source (currently mock, future: S3).
    
    Returns:
        List of scheme dictionaries
        
    Raises:
        Exception: If scheme loading fails
    """
    # TODO: Replace with S3 integration
    # Expected S3 implementation:
    # 1. Connect to S3 bucket (config.S3_BUCKET_NAME)
    # 2. List objects with prefix "schemes/"
    # 3. Download and parse JSON files
    # 4. Validate schema
    # 5. Sort by scheme_id for determinism
    
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
                    "explanation": "Annual income must be less than 1 lakh"
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
                    "explanation": "Age must be between 18 and 35"
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
    
    # Deterministic ordering guarantee
    schemes.sort(key=lambda s: s.get("scheme_id", ""))
    
    logger.info(f"Loaded {len(schemes)} schemes from source")
    return schemes


def load_schemes() -> List[Dict]:
    """
    Load schemes with caching strategy.
    
    Returns:
        List of scheme dictionaries
        
    Raises:
        Exception: If scheme loading fails and no cache available
    """
    global _scheme_cache, _cache_timestamp
    
    # Return from cache if valid
    if _is_cache_valid():
        logger.debug("Returning schemes from cache")
        return _scheme_cache
    
    # Load from source
    try:
        schemes = _load_schemes_from_source()
        
        # Update cache
        _scheme_cache = schemes
        _cache_timestamp = datetime.now(UTC)
        
        return schemes
    
    except Exception as e:
        logger.error(f"Failed to load schemes: {str(e)}")
        
        # Return stale cache if available
        if _scheme_cache is not None:
            logger.warning("Returning stale cache due to load failure")
            return _scheme_cache
        
        # No cache available, re-raise
        raise


def invalidate_cache() -> None:
    """
    Manually invalidate scheme cache.
    Used for testing or forced refresh.
    """
    global _scheme_cache, _cache_timestamp
    _scheme_cache = None
    _cache_timestamp = None
    logger.info("Scheme cache invalidated")
