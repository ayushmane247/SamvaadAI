# tests/test_integration.py
"""
Integration tests for the full eligibility evaluation flow.
Tests orchestration layer + engine + scheme loader without mocking.
"""

from orchestration.eligibility_service import evaluate_profile


def test_full_flow_farmer_eligible():
    """Test complete flow: farmer profile should match FARMER_SUPPORT scheme"""
    profile = {
        "occupation": "farmer",
        "age": 30,
        "income": 50000,
        "state": "Maharashtra"
    }
    
    result = evaluate_profile(profile)
    
    # Verify structure
    assert "eligible" in result
    assert "partially_eligible" in result
    assert "ineligible" in result
    
    # Verify farmer is eligible for FARMER_SUPPORT
    assert len(result["eligible"]) >= 1
    farmer_scheme = next((s for s in result["eligible"] if s["scheme_id"] == "FARMER_SUPPORT"), None)
    assert farmer_scheme is not None
    assert farmer_scheme["status"] == "eligible"
    assert "trace" in farmer_scheme


def test_full_flow_youth_eligible():
    """Test youth employment scheme eligibility"""
    profile = {
        "age": 25,
        "state": "Maharashtra",
        "occupation": "student"
    }
    
    result = evaluate_profile(profile)
    
    # Should be eligible for YOUTH_EMPLOYMENT
    youth_scheme = next((s for s in result["eligible"] if s["scheme_id"] == "YOUTH_EMPLOYMENT"), None)
    assert youth_scheme is not None
    assert youth_scheme["status"] == "eligible"


def test_full_flow_low_income_eligible():
    """Test low income support scheme eligibility"""
    profile = {
        "income": 50000,
        "age": 40,
        "state": "Karnataka"
    }
    
    result = evaluate_profile(profile)
    
    # Should be eligible for LOW_INCOME_SUPPORT
    low_income_scheme = next((s for s in result["eligible"] if s["scheme_id"] == "LOW_INCOME_SUPPORT"), None)
    assert low_income_scheme is not None
    assert low_income_scheme["status"] == "eligible"


def test_full_flow_multiple_eligible():
    """Test profile eligible for multiple schemes"""
    profile = {
        "occupation": "farmer",
        "age": 25,
        "income": 50000,
        "state": "Maharashtra"
    }
    
    result = evaluate_profile(profile)
    
    # Should be eligible for all three schemes
    assert len(result["eligible"]) == 3
    
    scheme_ids = [s["scheme_id"] for s in result["eligible"]]
    assert "FARMER_SUPPORT" in scheme_ids
    assert "YOUTH_EMPLOYMENT" in scheme_ids
    assert "LOW_INCOME_SUPPORT" in scheme_ids


def test_full_flow_ineligible():
    """Test profile that doesn't match any scheme"""
    profile = {
        "occupation": "doctor",
        "age": 50,
        "income": 500000,
        "state": "Karnataka"
    }
    
    result = evaluate_profile(profile)
    
    # Should have ineligible schemes
    assert len(result["ineligible"]) >= 1


def test_full_flow_partial_eligibility():
    """Test partial eligibility scenario"""
    profile = {
        "age": 25,
        "state": "Karnataka",  # Wrong state for YOUTH_EMPLOYMENT
        "occupation": "student"
    }
    
    result = evaluate_profile(profile)
    
    # YOUTH_EMPLOYMENT should be partially eligible (age matches, state doesn't)
    youth_scheme = next(
        (s for s in result["partially_eligible"] if s["scheme_id"] == "YOUTH_EMPLOYMENT"), 
        None
    )
    assert youth_scheme is not None
    assert youth_scheme["status"] == "partially_eligible"
    assert "missing_fields" in youth_scheme
    assert "guidance" in youth_scheme


def test_full_flow_empty_profile():
    """Test with empty profile"""
    profile = {}
    
    result = evaluate_profile(profile)
    
    # Should return results (all ineligible)
    assert "eligible" in result
    assert "partially_eligible" in result
    assert "ineligible" in result
    assert len(result["ineligible"]) >= 1


def test_full_flow_deterministic():
    """Test that same profile produces same results"""
    profile = {
        "occupation": "farmer",
        "age": 30,
        "income": 50000,
        "state": "Maharashtra"
    }
    
    result1 = evaluate_profile(profile)
    result2 = evaluate_profile(profile)
    result3 = evaluate_profile(profile)
    
    # Results should be identical
    assert result1 == result2 == result3


def test_full_flow_trace_present():
    """Test that trace is included in all results"""
    profile = {
        "occupation": "farmer",
        "age": 30
    }
    
    result = evaluate_profile(profile)
    
    # Check all categories have trace
    for scheme in result["eligible"]:
        assert "trace" in scheme
        assert len(scheme["trace"]) > 0
    
    for scheme in result["partially_eligible"]:
        assert "trace" in scheme
    
    for scheme in result["ineligible"]:
        assert "trace" in scheme


def test_full_flow_metadata_present():
    """Test that scheme metadata is preserved"""
    profile = {
        "occupation": "farmer"
    }
    
    result = evaluate_profile(profile)
    
    farmer_scheme = next((s for s in result["eligible"] if s["scheme_id"] == "FARMER_SUPPORT"), None)
    assert farmer_scheme is not None
    
    # Verify metadata fields
    assert "scheme_name" in farmer_scheme
    assert "benefit" in farmer_scheme
    assert "source_url" in farmer_scheme
    assert "last_verified_date" in farmer_scheme
    assert farmer_scheme["last_verified_date"] == "2025-02-15"


def test_orchestration_layer_no_side_effects():
    """Test that orchestration layer has no side effects"""
    profile = {"occupation": "farmer"}
    
    # Call multiple times
    result1 = evaluate_profile(profile)
    result2 = evaluate_profile(profile)
    
    # Results should be identical (no state mutation)
    assert result1 == result2
    
    # Profile should not be modified
    assert profile == {"occupation": "farmer"}


if __name__ == "__main__":
    import sys
    
    tests = [
        ("Full Flow: Farmer Eligible", test_full_flow_farmer_eligible),
        ("Full Flow: Youth Eligible", test_full_flow_youth_eligible),
        ("Full Flow: Low Income Eligible", test_full_flow_low_income_eligible),
        ("Full Flow: Multiple Eligible", test_full_flow_multiple_eligible),
        ("Full Flow: Ineligible", test_full_flow_ineligible),
        ("Full Flow: Partial Eligibility", test_full_flow_partial_eligibility),
        ("Full Flow: Empty Profile", test_full_flow_empty_profile),
        ("Full Flow: Deterministic", test_full_flow_deterministic),
        ("Full Flow: Trace Present", test_full_flow_trace_present),
        ("Full Flow: Metadata Present", test_full_flow_metadata_present),
        ("Orchestration: No Side Effects", test_orchestration_layer_no_side_effects),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            test_func()
            print(f"✓ {name}")
            passed += 1
        except AssertionError as e:
            print(f"✗ {name}: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {name}: Unexpected error - {e}")
            failed += 1
    
    print(f"\n{'='*50}")
    print(f"Integration Tests: {passed} passed, {failed} failed")
    print(f"{'='*50}")
    
    sys.exit(0 if failed == 0 else 1)
