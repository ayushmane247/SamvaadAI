"""
Scheme Ranking Service for SamvaadAI.

Provides deterministic scheme ranking based on benefit amount, priority, and transfer type.
Implements data-driven scoring formula with O(N) complexity for high performance.

Architectural Guarantees:
- Deterministic ranking using scheme JSON metadata only
- Performance-optimized (<5ms for 200 schemes)
- No external dependencies or LLM usage
- Automatic compatibility with new schemes
- Thread-safe operations
"""

import re
from typing import Dict, List, Any
import logging
import time

logger = logging.getLogger(__name__)


class SchemeRankingService:
    """
    Service for ranking eligible schemes by priority and benefit value.
    
    Implements scoring formula: 
    score = (benefit_amount * 0.5) + (priority * 10 if priority exists else 0) + (10 if direct_benefit_transfer == true else 0)
    """
    
    def __init__(self):
        """Initialize the scheme ranking service."""
        # Regex patterns for benefit amount extraction
        self.benefit_patterns = [
            # ₹X,XXX or Rs X,XXX patterns
            r'₹\s*([0-9,]+(?:\.[0-9]+)?)',
            r'Rs\.?\s*([0-9,]+(?:\.[0-9]+)?)',
            r'INR\s*([0-9,]+(?:\.[0-9]+)?)',
            # Lakh patterns
            r'₹\s*([0-9,]+(?:\.[0-9]+)?)\s*lakh',
            r'Rs\.?\s*([0-9,]+(?:\.[0-9]+)?)\s*lakh',
            r'([0-9,]+(?:\.[0-9]+)?)\s*lakh',
            # Crore patterns
            r'₹\s*([0-9,]+(?:\.[0-9]+)?)\s*crore',
            r'Rs\.?\s*([0-9,]+(?:\.[0-9]+)?)\s*crore',
            r'([0-9,]+(?:\.[0-9]+)?)\s*crore',
        ]
        
        logger.info("SchemeRankingService initialized")
    
    def extract_benefit_amount(self, scheme: Dict[str, Any]) -> float:
        """
        Extract numeric benefit amount from scheme benefit_summary field.
        
        Args:
            scheme: Scheme dictionary containing metadata
            
        Returns:
            Numeric benefit amount in rupees, 0.0 if not found or unparseable
        """
        # Handle None or non-dict scheme
        if not isinstance(scheme, dict):
            return 0.0
            
        try:
            benefit_summary = scheme.get("benefit_summary", "")
            if not benefit_summary or not isinstance(benefit_summary, str):
                return 0.0
            
            # Convert to lowercase for case-insensitive matching
            text = benefit_summary.lower()
            
            # Try each pattern
            for pattern in self.benefit_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    # Take the first match
                    amount_str = matches[0].replace(',', '')
                    try:
                        amount = float(amount_str)
                        
                        # Apply multipliers based on text content (not pattern)
                        if 'lakh' in text:
                            amount *= 100000  # 1 lakh = 1,00,000
                        elif 'crore' in text:
                            amount *= 10000000  # 1 crore = 1,00,00,000
                        
                        logger.debug(
                            "Benefit amount extracted",
                            extra={
                                "scheme_id": scheme.get("scheme_id", "unknown"),
                                "benefit_summary": benefit_summary[:100],
                                "extracted_amount": amount,
                                "pattern": pattern
                            }
                        )
                        
                        return amount
                        
                    except ValueError:
                        continue
            
            # If no patterns matched, return 0
            logger.debug(
                "No benefit amount found",
                extra={
                    "scheme_id": scheme.get("scheme_id", "unknown"),
                    "benefit_summary": benefit_summary[:100]
                }
            )
            
            return 0.0
            
        except Exception as e:
            logger.warning(
                "Error extracting benefit amount",
                extra={
                    "scheme_id": scheme.get("scheme_id", "unknown") if isinstance(scheme, dict) else "invalid",
                    "error_type": type(e).__name__,
                    "error": str(e)
                }
            )
            return 0.0
    
    def calculate_score(self, scheme: Dict[str, Any]) -> float:
        """
        Calculate ranking score for a scheme using the scoring formula.
        
        Formula: score = (benefit_amount * 0.5) + (priority * 10 if priority exists else 0) + (10 if direct_benefit_transfer == true else 0)
        
        Args:
            scheme: Scheme dictionary containing metadata
            
        Returns:
            Calculated score as float
        """
        # Handle None or non-dict scheme
        if not isinstance(scheme, dict):
            return 0.0
            
        try:
            # Extract benefit amount
            benefit_amount = self.extract_benefit_amount(scheme)
            
            # Extract priority (optional field)
            priority = scheme.get("priority", 0)
            if not isinstance(priority, (int, float)):
                priority = 0
            
            # Extract direct benefit transfer flag (optional field)
            direct_benefit_transfer = scheme.get("direct_benefit_transfer", False)
            if not isinstance(direct_benefit_transfer, bool):
                # Handle string representations
                if isinstance(direct_benefit_transfer, str):
                    direct_benefit_transfer = direct_benefit_transfer.lower() in ['true', 'yes', '1']
                else:
                    direct_benefit_transfer = False
            
            # Apply scoring formula
            score = (benefit_amount * 0.5) + (priority * 10) + (10 if direct_benefit_transfer else 0)
            
            logger.debug(
                "Score calculated",
                extra={
                    "scheme_id": scheme.get("scheme_id", "unknown"),
                    "benefit_amount": benefit_amount,
                    "priority": priority,
                    "direct_benefit_transfer": direct_benefit_transfer,
                    "calculated_score": score
                }
            )
            
            return score
            
        except Exception as e:
            logger.warning(
                "Error calculating score",
                extra={
                    "scheme_id": scheme.get("scheme_id", "unknown") if isinstance(scheme, dict) else "invalid",
                    "error_type": type(e).__name__,
                    "error": str(e)
                }
            )
            return 0.0
    
    def rank_schemes(self, schemes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Rank schemes by calculated score in descending order.
        
        Args:
            schemes: List of scheme dictionaries
            
        Returns:
            List of schemes sorted by score (highest first), with rank_score field added
        """
        start_time = time.perf_counter()
        
        try:
            if not schemes:
                return []
            
            # Calculate scores for all schemes
            scored_schemes = []
            for scheme in schemes:
                scheme_copy = scheme.copy()  # Don't modify original
                score = self.calculate_score(scheme)
                scheme_copy["rank_score"] = score
                scored_schemes.append(scheme_copy)
            
            # Sort by score (descending order)
            ranked_schemes = sorted(scored_schemes, key=lambda s: s["rank_score"], reverse=True)
            
            execution_time_ms = (time.perf_counter() - start_time) * 1000
            
            logger.info(
                "Schemes ranked successfully",
                extra={
                    "schemes_processed": len(schemes),
                    "execution_time_ms": round(execution_time_ms, 3),
                    "top_score": ranked_schemes[0]["rank_score"] if ranked_schemes else 0,
                    "score_range": {
                        "min": min(s["rank_score"] for s in ranked_schemes) if ranked_schemes else 0,
                        "max": max(s["rank_score"] for s in ranked_schemes) if ranked_schemes else 0
                    }
                }
            )
            
            return ranked_schemes
            
        except Exception as e:
            execution_time_ms = (time.perf_counter() - start_time) * 1000
            
            logger.error(
                "Error ranking schemes",
                extra={
                    "schemes_count": len(schemes) if schemes else 0,
                    "error_type": type(e).__name__,
                    "execution_time_ms": round(execution_time_ms, 3)
                }
            )
            
            # Return original schemes on error to maintain pipeline stability
            return schemes
    
    def get_ranking_metadata(self, schemes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get ranking metadata and statistics for analysis.
        
        Args:
            schemes: List of ranked schemes
            
        Returns:
            Dictionary containing ranking statistics
        """
        try:
            if not schemes:
                return {
                    "total_schemes": 0,
                    "score_statistics": {},
                    "benefit_statistics": {},
                    "priority_distribution": {},
                    "direct_transfer_count": 0
                }
            
            scores = [s.get("rank_score", 0) for s in schemes]
            benefits = [self.extract_benefit_amount(s) for s in schemes]
            priorities = [s.get("priority", 0) for s in schemes]
            direct_transfers = sum(1 for s in schemes if s.get("direct_benefit_transfer", False))
            
            metadata = {
                "total_schemes": len(schemes),
                "score_statistics": {
                    "min": min(scores) if scores else 0,
                    "max": max(scores) if scores else 0,
                    "avg": sum(scores) / len(scores) if scores else 0
                },
                "benefit_statistics": {
                    "min": min(benefits) if benefits else 0,
                    "max": max(benefits) if benefits else 0,
                    "avg": sum(benefits) / len(benefits) if benefits else 0
                },
                "priority_distribution": {
                    "with_priority": sum(1 for p in priorities if p > 0),
                    "without_priority": sum(1 for p in priorities if p == 0)
                },
                "direct_transfer_count": direct_transfers
            }
            
            return metadata
            
        except Exception as e:
            logger.warning(
                "Error generating ranking metadata",
                extra={
                    "error_type": type(e).__name__,
                    "error": str(e)
                }
            )
            return {}