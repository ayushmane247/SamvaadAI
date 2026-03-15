"""
Adaptive Question Engine for SamvaadAI.

Intelligently determines which profile field to ask next based on 
scheme unlock potential through simulation-based analysis.

Architecture:
- Simulates possible values for each missing field
- Evaluates eligibility impact for each simulation
- Ranks fields by maximum scheme unlock potential
- Returns highest priority field with deterministic ordering

Performance Constraints:
- Must complete within 10ms per query
- Maximum 10 simulations per field
- Uses deep copy for safe profile simulation
- Deterministic ranking for stable results
"""

import copy
import time
from typing import Dict, List, Any, Optional, Tuple
import logging

from services.question_priority_service import QuestionPriorityService
from orchestration.eligibility_service import evaluate_profile

logger = logging.getLogger(__name__)


class FieldRanking:
    """Data class for field ranking results."""
    
    def __init__(self, field: str, priority_score: int, simulations_run: int):
        self.field = field
        self.priority_score = priority_score
        self.simulations_run = simulations_run
    
    def __repr__(self):
        return f"FieldRanking(field='{self.field}', score={self.priority_score}, sims={self.simulations_run})"


class AdaptiveQuestionEngine:
    """
    Adaptive Question Engine that determines optimal question ordering
    through eligibility simulation and impact analysis.
    
    Core Algorithm:
    1. Identify missing profile fields
    2. For each missing field:
       - Simulate possible values (max 10)
       - Run eligibility evaluation for each simulation
       - Count newly eligible schemes vs baseline
       - Record maximum unlock count as field priority
    3. Rank fields by priority score (desc) then alphabetically
    4. Return highest priority field with question text
    """
    
    def __init__(self):
        """Initialize the adaptive question engine."""
        self.priority_service = QuestionPriorityService()
        logger.info("AdaptiveQuestionEngine initialized")
    
    def _get_baseline_eligibility(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get baseline eligibility evaluation for current profile.
        
        Args:
            profile: Current user profile
            
        Returns:
            Baseline eligibility evaluation result
        """
        try:
            return evaluate_profile(profile)
        except Exception as e:
            logger.error(f"Baseline eligibility evaluation failed: {e}")
            return {"eligible": [], "partially_eligible": [], "ineligible": []}
    
    def _simulate_field_impact(
        self, 
        profile: Dict[str, Any], 
        field: str, 
        baseline_eligible_count: int
    ) -> Tuple[int, int]:
        """
        Simulate impact of a field by testing different values.
        
        Args:
            profile: Current user profile (will be deep copied)
            field: Field name to simulate
            baseline_eligible_count: Number of currently eligible schemes
            
        Returns:
            Tuple of (max_newly_eligible_count, simulations_run)
        """
        simulation_values = self.priority_service.get_simulation_values(field)
        if not simulation_values:
            logger.debug(f"No simulation values for field: {field}")
            return 0, 0
        
        max_newly_eligible = 0
        simulations_run = 0
        
        for value in simulation_values:
            try:
                # Deep copy profile to avoid mutation
                sim_profile = copy.deepcopy(profile)
                sim_profile[field] = value
                
                # Evaluate eligibility with simulated value
                sim_result = evaluate_profile(sim_profile)
                sim_eligible_count = len(sim_result.get("eligible", []))
                
                # Calculate newly eligible schemes
                newly_eligible = max(0, sim_eligible_count - baseline_eligible_count)
                max_newly_eligible = max(max_newly_eligible, newly_eligible)
                
                simulations_run += 1
                
                logger.debug(
                    f"Simulation {field}={value}: "
                    f"eligible={sim_eligible_count}, newly={newly_eligible}"
                )
                
            except Exception as e:
                logger.warning(f"Simulation failed for {field}={value}: {e}")
                continue
        
        logger.debug(
            f"Field {field}: max_newly_eligible={max_newly_eligible}, "
            f"simulations_run={simulations_run}"
        )
        
        return max_newly_eligible, simulations_run
    
    def _rank_fields(
        self, 
        profile: Dict[str, Any], 
        missing_fields: List[str]
    ) -> List[FieldRanking]:
        """
        Rank missing fields by scheme unlock potential.
        
        Args:
            profile: Current user profile
            missing_fields: List of missing field names
            
        Returns:
            List of FieldRanking objects sorted by priority
        """
        start_time = time.time()
        
        # Get baseline eligibility
        baseline_result = self._get_baseline_eligibility(profile)
        baseline_eligible_count = len(baseline_result.get("eligible", []))
        
        logger.debug(f"Baseline eligible schemes: {baseline_eligible_count}")
        
        # Simulate impact for each missing field
        rankings = []
        total_simulations = 0
        
        for field in missing_fields:
            if not self.priority_service.validate_field(field):
                logger.debug(f"Skipping unsupported field: {field}")
                continue
            
            max_newly_eligible, simulations_run = self._simulate_field_impact(
                profile, field, baseline_eligible_count
            )
            
            ranking = FieldRanking(
                field=field,
                priority_score=max_newly_eligible,
                simulations_run=simulations_run
            )
            rankings.append(ranking)
            total_simulations += simulations_run
        
        # Sort by priority score (descending) then alphabetically for deterministic results
        rankings.sort(key=lambda r: (-r.priority_score, r.field))
        
        elapsed_ms = (time.time() - start_time) * 1000
        
        logger.info(
            f"Field ranking completed",
            extra={
                "fields_analyzed": len(rankings),
                "total_simulations": total_simulations,
                "elapsed_ms": round(elapsed_ms, 2),
                "baseline_eligible": baseline_eligible_count
            }
        )
        
        return rankings
    
    def get_next_question(
        self, 
        profile: Dict[str, Any], 
        missing_fields: Optional[List[str]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get the next best question to ask based on scheme unlock potential.
        
        Args:
            profile: Current user profile
            missing_fields: Optional list of missing fields (auto-detected if None)
            
        Returns:
            Question dict with field, priority_score, and question_text, or None
        """
        start_time = time.time()
        
        try:
            # Auto-detect missing fields if not provided
            if missing_fields is None:
                all_fields = self.priority_service.get_all_simulatable_fields()
                missing_fields = [f for f in all_fields if f not in profile or profile[f] is None]
            
            # Filter to only simulatable fields
            simulatable_missing = [
                f for f in missing_fields 
                if self.priority_service.validate_field(f)
            ]
            
            if not simulatable_missing:
                logger.info("No simulatable missing fields found")
                return None
            
            logger.debug(f"Analyzing {len(simulatable_missing)} missing fields: {simulatable_missing}")
            
            # Rank fields by impact
            rankings = self._rank_fields(profile, simulatable_missing)
            
            if not rankings:
                logger.warning("No field rankings generated")
                return None
            
            # Select highest priority field
            best_ranking = rankings[0]
            question_text = self.priority_service.get_question_text(best_ranking.field)
            
            elapsed_ms = (time.time() - start_time) * 1000
            
            # Log metrics
            logger.info(
                f"Adaptive question selected: {best_ranking.field}",
                extra={
                    "field": best_ranking.field,
                    "priority_score": best_ranking.priority_score,
                    "simulations_run": sum(r.simulations_run for r in rankings),
                    "execution_time_ms": round(elapsed_ms, 2),
                    "field_rankings": [
                        {"field": r.field, "score": r.priority_score} 
                        for r in rankings[:5]  # Top 5 for logging
                    ]
                }
            )
            
            return {
                "field": best_ranking.field,
                "priority_score": best_ranking.priority_score,
                "question_text": question_text,
                "metadata": {
                    "simulations_run": best_ranking.simulations_run,
                    "execution_time_ms": round(elapsed_ms, 2),
                    "fields_analyzed": len(rankings)
                }
            }
            
        except Exception as e:
            elapsed_ms = (time.time() - start_time) * 1000
            logger.error(
                f"Adaptive question selection failed",
                extra={
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "execution_time_ms": round(elapsed_ms, 2)
                },
                exc_info=True
            )
            return None
    
    def get_field_rankings(
        self, 
        profile: Dict[str, Any], 
        missing_fields: Optional[List[str]] = None
    ) -> List[FieldRanking]:
        """
        Get detailed field rankings for analysis/debugging.
        
        Args:
            profile: Current user profile
            missing_fields: Optional list of missing fields
            
        Returns:
            List of FieldRanking objects sorted by priority
        """
        if missing_fields is None:
            all_fields = self.priority_service.get_all_simulatable_fields()
            missing_fields = [f for f in all_fields if f not in profile or profile[f] is None]
        
        simulatable_missing = [
            f for f in missing_fields 
            if self.priority_service.validate_field(f)
        ]
        
        return self._rank_fields(profile, simulatable_missing)