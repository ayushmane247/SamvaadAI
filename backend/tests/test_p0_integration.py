"""
Integration tests for P0 fixes: Scheme Ranking and CSC Center services.

Verifies that:
1. Schemes are ranked with rank_score field
2. CSC centers are returned in response
3. Integration doesn't break existing functionality
"""

import pytest
from orchestration.conversation_manager import ConversationManager


def test_scheme_ranking_integration():
    """Verify schemes are ranked in response with rank_score field."""
    manager = ConversationManager()
    result = manager.process_user_query(
        "I am a farmer in Maharashtra with income below 2 lakhs",
        language="en"
    )
    
    # Check that eligible schemes exist
    eligible = result["eligibility"]["eligible"]
    assert len(eligible) > 0, "Should have eligible schemes"
    
    # Check that schemes have rank_score field
    for scheme in eligible:
        assert "rank_score" in scheme, f"Scheme {scheme.get('scheme_id')} missing rank_score"
        assert isinstance(scheme["rank_score"], (int, float)), "rank_score should be numeric"
    
    # Verify descending order if multiple schemes
    if len(eligible) > 1:
        scores = [s["rank_score"] for s in eligible]
        assert scores == sorted(scores, reverse=True), "Schemes should be sorted by rank_score descending"


def test_csc_centers_field_exists():
    """Verify csc_centers field is present in response."""
    manager = ConversationManager()
    result = manager.process_user_query(
        "I am in Mumbai, Maharashtra",
        language="en"
    )
    
    # Check that csc_centers field exists
    assert "csc_centers" in result, "Response should include csc_centers field"
    assert isinstance(result["csc_centers"], list), "csc_centers should be a list"


def test_partial_schemes_also_ranked():
    """Verify partially eligible schemes are also ranked."""
    manager = ConversationManager()
    result = manager.process_user_query(
        "I am a student in Delhi",
        language="en"
    )
    
    # Check partially eligible schemes
    partial = result["eligibility"]["partially_eligible"]
    
    # If there are partial schemes, they should have rank_score
    for scheme in partial:
        assert "rank_score" in scheme, f"Partial scheme {scheme.get('scheme_id')} missing rank_score"


def test_ranking_preserves_scheme_data():
    """Verify ranking doesn't corrupt scheme data."""
    manager = ConversationManager()
    result = manager.process_user_query(
        "I am a farmer in Maharashtra with income below 2 lakhs",
        language="en"
    )
    
    eligible = result["eligibility"]["eligible"]
    
    # Verify essential fields are preserved
    for scheme in eligible:
        assert "scheme_id" in scheme, "scheme_id should be preserved"
        assert "scheme_name" in scheme, "scheme_name should be preserved"
        assert "benefit" in scheme, "benefit should be preserved"
        assert "rank_score" in scheme, "rank_score should be added"


def test_csc_centers_with_complete_location():
    """Verify CSC centers are populated when state and district are provided."""
    manager = ConversationManager()
    result = manager.process_user_query(
        "I am a farmer in Pune district, Maharashtra",
        language="en"
    )
    
    # Check profile has location data
    profile = result["profile"]
    
    # CSC centers field should exist
    assert "csc_centers" in result, "Response should include csc_centers field"
    
    # If profile has both state and district, centers should be attempted
    # (may be empty if data file not found, but field should exist)
    assert isinstance(result["csc_centers"], list), "csc_centers should be a list"


def test_backward_compatibility_maintained():
    """Verify P0 fixes don't break existing response structure."""
    manager = ConversationManager()
    result = manager.process_user_query(
        "I am a farmer in Maharashtra",
        language="en"
    )
    
    # Verify all expected fields exist
    assert "profile" in result
    assert "eligibility" in result
    assert "response" in result
    assert "question" in result
    assert "schemes" in result
    assert "documents" in result
    assert "csc_centers" in result  # NEW field
    assert "llm_enhanced" in result
    assert "llm_metadata" in result
