# orchestration/eligibility_service.py
"""
Orchestration layer for eligibility evaluation.
Coordinates between scheme loader and eligibility engine.

Architectural Guarantees:
- Deterministic evaluation (same input → same output)
- No business logic (pure orchestration)
- Latency tracking for observability
- Graceful error handling

Output Contract (from design.md):
- eligible: List of eligible schemes with trace
- partially_eligible: List of partially eligible schemes with guidance
- ineligible: List of ineligible schemes with reasons

Deterministic Ordering:
- All output lists are sorted by scheme_id
- Guaranteed by engine implementation
- No reliance on Python dict ordering
"""

import time
from typing import Dict, List
from eligibility_engine.engine import evaluate
from scheme_service.scheme_loader import load_schemes
from core.logging_config import logger
from core.config import config


# Fields that represent application process steps, not conversational profile attributes.
# These cannot be collected via chat and should be excluded from eligibility scoring.
_PROCESS_ONLY_FIELDS = {"work_days", "registration", "application_platform"}

# Maps age_group categorical values to numeric midpoints for eligibility evaluation
_AGE_GROUP_MIDPOINTS = {
    "minor":  14,
    "18-25":  21,
    "26-35":  30,
    "36-45":  40,
    "46-60":  52,
    "60+":    65,
}


def _pre_normalize_profile(profile: dict) -> dict:
    """
    Derive missing numeric/categorical fields from categorical profile fields.
    Does NOT mutate the original profile.

    Derivations:
    - age_group → age (midpoint), if age not already set
    - land_holding → farmer_category (small/marginal/large), if not already set
    """
    normalized = dict(profile)

    # Derive numeric age from age_group
    if "age" not in normalized and "age_group" in normalized:
        midpoint = _AGE_GROUP_MIDPOINTS.get(normalized["age_group"])
        if midpoint is not None:
            normalized["age"] = midpoint

    # Derive farmer_category from land_holding
    if "farmer_category" not in normalized and "land_holding" in normalized:
        holding = normalized["land_holding"]
        try:
            holding_f = float(holding)
            if holding_f <= 1.0:
                normalized["farmer_category"] = "marginal"
            elif holding_f <= 2.0:
                normalized["farmer_category"] = "small"
            else:
                normalized["farmer_category"] = "large"
        except (TypeError, ValueError):
            pass

    return normalized


def _filter_process_criteria(schemes: List[dict]) -> List[dict]:
    """
    Return a copy of schemes with process-only criteria removed.

    Process-only fields (work_days, registration, application_platform) cannot
    be collected conversationally. Removing them lets the engine evaluate the
    remaining profile-based criteria correctly, surfacing schemes as
    partially_eligible rather than ineligible when only process steps are missing.
    """
    filtered = []
    for scheme in schemes:
        criteria = scheme.get("eligibility_criteria", [])
        profile_criteria = [c for c in criteria if c.get("field") not in _PROCESS_ONLY_FIELDS]
        if len(profile_criteria) == len(criteria):
            # No change needed — avoid unnecessary copy
            filtered.append(scheme)
        else:
            filtered.append({**scheme, "eligibility_criteria": profile_criteria})
    return filtered


def evaluate_profile(profile: dict) -> dict:
    """
    Orchestrates eligibility evaluation by loading schemes and calling engine.
    
    Workflow:
    1. Load schemes (with caching)
    2. Call deterministic engine
    3. Track latency
    4. Return result (no transformation)
    
    Args:
        profile: User profile dictionary with attributes
        
    Returns:
        Evaluation result from engine (eligible, partially_eligible, ineligible)
        
    Raises:
        Exception: If scheme loading or evaluation fails
    """
    start_time = time.time()
    
    try:
        # Load schemes (cached)
        schemes = load_schemes()

        # Pre-normalize profile: derive age from age_group, farmer_category from land_holding
        normalized_profile = _pre_normalize_profile(profile)

        # Filter process-only criteria so they don't block conversational eligibility
        filtered_schemes = _filter_process_criteria(schemes)
        
        # Deterministic evaluation
        result = evaluate(normalized_profile, filtered_schemes)
        
        # Track latency
        if config.ENABLE_LATENCY_TRACKING:
            latency_ms = (time.time() - start_time) * 1000
            logger.info(
                f"Evaluation completed in {latency_ms:.2f}ms for {len(schemes)} schemes",
                extra={"latency_ms": latency_ms, "evaluation_count": len(schemes)}
            )
            
            # Warn if exceeding threshold
            if latency_ms > config.EVALUATION_LATENCY_THRESHOLD_MS:
                logger.warning(
                    f"Evaluation latency {latency_ms:.2f}ms exceeds threshold "
                    f"{config.EVALUATION_LATENCY_THRESHOLD_MS}ms"
                )
        
        return result
    
    except Exception as e:
        logger.error(f"Evaluation failed: {str(e)}", exc_info=True)
        raise

