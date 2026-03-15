"""
Tests for Scheme Explainability Service.

Tests the deterministic explanation generation for scheme eligibility.
"""

import pytest
from services.scheme_explainability_service import explainability_service


class TestSchemeExplainabilityService:
    """Test cases for scheme explainability service."""
    
    def test_generate_explanation_basic(self):
        """Test basic explanation generation for a simple scheme."""
        profile = {
            "occupation": "farmer",
            "state": "Maharashtra",
            "income_range": "below_1l"
        }
        
        scheme = {
            "scheme_id": "PM_KISAN",
            "name": "PM Kisan Samman Nidhi",
            "eligibility_criteria": [
                {
                    "field": "occupation",
                    "operator": "equals",
                    "value": "farmer",
                    "explanation": "Must be a farmer"
                },
                {
                    "field": "state",
                    "operator": "equals",
                    "value": "Maharashtra",
                    "explanation": "Must be from Maharashtra"
                }
            ]
        }
        
        explanations = explainability_service.generate_explanation(profile, scheme, "en")
        
        assert len(explanations) == 2
        assert "✔ Must be a farmer" in explanations
        assert "✔ Must be from Maharashtra" in explanations
    
    def test_generate_explanation_multilingual(self):
        """Test explanation generation in different languages."""
        profile = {"occupation": "farmer"}
        scheme = {
            "scheme_id": "TEST",
            "eligibility_criteria": [
                {
                    "field": "occupation",
                    "operator": "equals", 
                    "value": "farmer",
                    "explanation": ""
                }
            ]
        }
        
        # Test English
        explanations_en = explainability_service.generate_explanation(profile, scheme, "en")
        assert len(explanations_en) == 1
        assert "work as a farmer" in explanations_en[0]
        
        # Test Hindi
        explanations_hi = explainability_service.generate_explanation(profile, scheme, "hi")
        assert len(explanations_hi) == 1
        assert "farmer" in explanations_hi[0]
    
    def test_performance_requirement(self):
        """Test that explanation generation completes under 5ms."""
        import time
        
        profile = {
            "occupation": "farmer",
            "state": "Maharashtra", 
            "income_range": "below_1l",
            "age_group": "26-35",
            "gender": "male"
        }
        
        scheme = {
            "scheme_id": "COMPLEX_SCHEME",
            "eligibility_criteria": [
                {"field": "occupation", "operator": "equals", "value": "farmer", "explanation": "Must be farmer"},
                {"field": "state", "operator": "equals", "value": "Maharashtra", "explanation": "Must be from Maharashtra"},
                {"field": "income_range", "operator": "equals", "value": "below_1l", "explanation": "Income below 1 lakh"},
                {"field": "age_group", "operator": "equals", "value": "26-35", "explanation": "Age 26-35"},
                {"field": "gender", "operator": "equals", "value": "male", "explanation": "Must be male"}
            ]
        }
        
        start_time = time.time()
        explanations = explainability_service.generate_explanation(profile, scheme, "en")
        execution_time_ms = (time.time() - start_time) * 1000
        
        assert execution_time_ms < 5.0  # Must complete under 5ms
        assert len(explanations) == 5  # All rules should match
    
    def test_no_matching_rules(self):
        """Test explanation generation when no rules match."""
        profile = {"occupation": "student"}
        scheme = {
            "scheme_id": "FARMER_ONLY",
            "eligibility_criteria": [
                {
                    "field": "occupation",
                    "operator": "equals",
                    "value": "farmer",
                    "explanation": "Must be a farmer"
                }
            ]
        }
        
        explanations = explainability_service.generate_explanation(profile, scheme, "en")
        assert len(explanations) == 0  # No matching rules
    
    def test_boolean_field_explanations(self):
        """Test explanation generation for boolean fields."""
        profile = {"bank_account": True, "bpl_status": False}
        scheme = {
            "scheme_id": "BANK_REQUIRED",
            "eligibility_criteria": [
                {
                    "field": "bank_account",
                    "operator": "equals",
                    "value": True,
                    "explanation": ""
                }
            ]
        }
        
        explanations = explainability_service.generate_explanation(profile, scheme, "en")
        assert len(explanations) == 1
        assert "bank account" in explanations[0].lower()
    
    def test_failsafe_behavior(self):
        """Test that service handles errors gracefully."""
        profile = {"occupation": "farmer"}
        
        # Invalid scheme structure
        invalid_scheme = {"scheme_id": "INVALID"}  # No eligibility_criteria
        
        explanations = explainability_service.generate_explanation(profile, invalid_scheme, "en")
        assert explanations == []  # Should return empty list, not crash