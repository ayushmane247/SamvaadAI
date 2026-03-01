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
from typing import Dict
from eligibility_engine.engine import evaluate
from scheme_service.scheme_loader import load_schemes
from core.logging_config import logger
from core.config import config


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
        
        # Deterministic evaluation
        result = evaluate(profile, schemes)
        
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

